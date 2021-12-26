import os
import requests
import rest_framework
from django.contrib import messages
from django.contrib.auth import login
from django.core.files.base import ContentFile
from django.db.models import Prefetch
from django.shortcuts import redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, renderer_classes
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from .models import CommonUser
from .costume_serializers import FullUserSerializer
from .serializers import UserSerializer
from group.models import Contract
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.sites.models import Site


current_site = Site.objects.get_current()
KAKAO_CLIENT_ID = os.environ.get('KAKAO_ID')
KAKAO_REDIRECT_URI = current_site.domain+'/api/common/kakao-callback/'
KAKAO_SECRET=os.environ.get('KAKAO_SECRET')
RESPONSE_TYPE = 'code'


class CommonUserViewSet(viewsets.ModelViewSet):
    queryset = CommonUser.objects.all()
    serializer_class = FullUserSerializer
    parser_classes = [MultiPartParser]

    def get_queryset(self):
        company = self.request.query_params.get('company')
        queryset = CommonUser.objects.prefetch_related(
            Prefetch('contract', queryset=Contract.objects.filter(company=company))).order_by('-date_joined')

        return queryset

    def partial_update(self, request, pk=None, *args, **kwargs):
        data = self.request.data
        instance = self.get_object()
        serializer = UserSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def delete_profile_image(self, request, pk=None):
        user = self.get_object()
        user.image.delete(save=True)
        user.save()
        return Response(data={'id': pk}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_profile_image(self, request, pk=None):
        user = self.get_object()
        if request.FILES:
            user.image = request.FILES
        serializer = UserSerializer(user, data=user, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def kakao_login(request):
    try:
        if request.user.is_authenticated:
            raise Exception('이미 로그인한 유저입니다.')
        return redirect(
            f'https://kauth.kakao.com/oauth/authorize?client_id={KAKAO_CLIENT_ID}&redirect_uri={KAKAO_REDIRECT_URI}'
            f'&response_type={RESPONSE_TYPE}'
        )
    except Exception as e:
        print(e)
        messages.error(request, e)
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class KakaoException(Exception):
    pass


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def kakao_login_callback(request):
    try:
        if request.user.is_authenticated:
            raise KakaoException('이미 로그인한 유저입니다.')
        code = request.GET.get('code', None)
        if code is None:
            KakaoException('코드를 불러올 수 없습니다.')
        request_access_token = requests.post(
            f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={KAKAO_CLIENT_ID}'
            f'&redirect_uri={KAKAO_REDIRECT_URI}&code={code}&client_secret={KAKAO_SECRET}',
            headers={'Accept': 'application/json'},
        )
        access_token_json = request_access_token.json()
        error = access_token_json.get('error', None)
        if error is not None:
            KakaoException('access token을 가져올수 없습니다.')
        access_token = access_token_json.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_request = requests.post('https://kapi.kakao.com/v2/user/me',
                                        headers=headers,
                                        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        profile = kakao_account.get('profile')

        nickname = profile.get('nickname', None)
        avatar_url = profile.get('profile_image_url', None)
        email = kakao_account.get('email', None)

        try:
            user = CommonUser.objects.get(email=email)
        except CommonUser.DoesNotExist:
            user = None
        if user is not None:
            if user.login_method != CommonUser.LOGIN_KAKAO:
                KakaoException(f'{user.login_method}로 로그인 해주세요')
        else:
            user = CommonUser(
                email=email,
                nickname=nickname,
                login_method=CommonUser.LOGIN_KAKAO
            )
            if avatar_url is not None:
                avatar_request = requests.post(avatar_url)
                user.image = ContentFile(avatar_request.content)
            user.set_unusable_password()
            user.save()
        messages.success(request, f'{user.email} 카카오 로그인 성공')
        login(request, user, backend="django.contrib.auth.backends.ModelBackend",)
        return Response({'message': '로그인 성공'})
    except KakaoException as e:
        print(e)
        messages.error(request, e)
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GoogleLogin(SocialLoginView):
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000"
    client_class = OAuth2Client


@csrf_exempt
def google_token():
    if 'code' not in rest_framework.request.body.decode():
        from rest_framework_simplejwt.settings import api_settings as jwt_settings
        from rest_framework_simplejwt.views import TokenRefreshView

        class RefreshAuth(TokenRefreshView):
            def post(self, *args, **kwargs):
                self.request.data._mutable = True
                self.request.data['refresh'] = self.request.data.get('refresh_token')
                self.request.data._mutable = False
                response = super().post(self.request, *args, **kwargs)
                response.data['refresh_token'] = response.data['refresh']
                response.data['access_token'] = response.data['access']
                return response

        return RefreshAuth
    else:
        return GoogleLogin
