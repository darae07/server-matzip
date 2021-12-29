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
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.sites.models import Site
from dj_rest_auth import views
from dj_rest_auth.serializers import JWTSerializer

current_site = Site.objects.get_current()
KAKAO_CLIENT_ID = os.environ.get('KAKAO_ID')
KAKAO_REDIRECT_URI = current_site.domain + '/api/common/kakao-callback/'
KAKAO_SECRET = os.environ.get('KAKAO_SECRET')
RESPONSE_TYPE = 'code'


class CommonUserViewSet(viewsets.ModelViewSet):
    queryset = CommonUser.objects.all()
    serializer_class = FullUserSerializer

    def get_queryset(self):
        company = self.request.query_params.get('company')
        queryset = CommonUser.objects.prefetch_related(
            Prefetch('contract', queryset=Contract.objects.filter(company=company))).order_by('-date_joined')

        return queryset

    def partial_update(self, request, pk=None, *args, **kwargs):
        data = self.request.data
        # if 'email' in data:
        #     user = request.user
        #     if user.email != data
        instance = self.get_object()
        serializer = UserSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['patch'])
    def update_profile(self, request):
        user = request.user
        data = request.data
        if 'email' in data:
            if user.email == data['email']:
                data.pop('email')
            else:
                try:
                    same_email = CommonUser.objects.get(email=data['email'])
                    if same_email:
                        return Response({'message': '이미 사용중인 이메일 입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                except CommonUser.DoesNotExist:
                    pass
        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'])
    def delete_profile_image(self, request, pk=None):
        user = self.request.user
        user.image.delete(save=True)
        user.save()
        return Response(data={'id': pk}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_profile_image(self, request, pk=None):
        user = self.request.user
        data = {}
        if request.FILES:
            data['image'] = request.FILES['image']
        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class AlertException(Exception):
    pass


class TokenException(Exception):
    pass


class LoginView(views.LoginView):
    def post(self, request, *args, **kwargs):
        try:
            user = CommonUser.objects.get(email=request.data['email'])
        except CommonUser.DoesNotExist:
            user = None
        if user is not None:
            if user.login_method != CommonUser.LOGIN_EMAIL:
                return Response({'message': f'{user.login_method}로 로그인 해주세요'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        views.LoginView.serializer = super(LoginView, self).get_serializer(data=request.data)
        views.LoginView.serializer.is_valid(raise_exception=True)
        super(LoginView, self).login()
        return super(LoginView, self).get_response()


class LogoutView(views.LogoutView):
    def post(self, request, *args, **kwargs):
        user = request.user
        if user.login_method == CommonUser.LOGIN_KAKAO:
            return kakao_logout(request)
        return super(LogoutView, self).logout(request)


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


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def kakao_login_callback(request):
    try:
        if request.user.is_authenticated:
            raise AlertException('이미 로그인한 유저입니다.')
        code = request.GET.get('code', None)
        if code is None:
            TokenException('코드를 불러올 수 없습니다.')
        request_access_token = requests.post(
            f'https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={KAKAO_CLIENT_ID}'
            f'&redirect_uri={KAKAO_REDIRECT_URI}&code={code}&client_secret={KAKAO_SECRET}',
            headers={'Accept': 'application/json'},
        )
        access_token_json = request_access_token.json()
        error = access_token_json.get('error', None)
        if error is not None:
            TokenException('access token을 가져올수 없습니다.')
        access_token = access_token_json.get('access_token')
        refresh_token = access_token_json.get('refresh_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        profile_request = requests.post('https://kapi.kakao.com/v2/user/me',
                                        headers=headers,
                                        )
        profile_json = profile_request.json()
        kakao_account = profile_json.get('kakao_account')
        profile = kakao_account.get('profile')

        nickname = profile.get('nickname', None)
        email = kakao_account.get('email', None)

        if email is None:
            AlertException('카카오계정(이메일) 제공 동의에 체크해 주세요.')

        try:
            user = CommonUser.objects.get(email=email)
        except CommonUser.DoesNotExist:
            user = None
        if user is not None:
            if user.login_method != CommonUser.LOGIN_KAKAO:
                AlertException(f'{user.login_method}로 로그인 해주세요')
        else:
            user = CommonUser(
                email=email,
                nickname=nickname,
                login_method=CommonUser.LOGIN_KAKAO
            )

            user.set_unusable_password()
            user.save()
        messages.success(request, f'{user.email} 카카오 로그인 성공')
        login(request, user, backend="django.contrib.auth.backends.ModelBackend", )
        data = {
            'user': user,
            'access_token': access_token,
            'refresh_token': refresh_token,
        }
        serializer = JWTSerializer(data)
        return Response({'message': '로그인 성공', **serializer.data}, status=status.HTTP_200_OK)
    except AlertException as e:
        print(e)
        messages.error(request, e)
        # 유저에게 알림
        return Response({'message': str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)
    except TokenException as e:
        print(e)
        # 개발 단계에서 확인
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def kakao_logout(request):
    try:
        access_token = request.META.get('HTTP_KAKAOTOKEN')
        headers = {'Authorization': f'Bearer {access_token}'}
        logout_request = requests.post('https://kapi.kakao.com/v1/user/logout', headers=headers)
        logout_request_json = logout_request.json()
        error = logout_request_json.get('error', None)
        code = logout_request_json.get('code')
        print(error, code)
        if error is not None:
            AlertException('로그아웃 실패')
        return Response({'message': '로그아웃 성공'})
    except AlertException as e:
        messages.error(request, e)
        # 유저에게 알림
        return Response({'message': str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)


@api_view(('POST',))
@renderer_classes((JSONRenderer,))
def kakao_token_refresh(request):
    token_refresh = requests.post('https://kauth.kakao.com/oauth/token', data={
        'grant_type': 'refresh_token',
        'client_id': KAKAO_CLIENT_ID,
        'refresh_token': request.data['refresh_token']
    }, headers={'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'}, )
    access_token_json = token_refresh.json()
    error = access_token_json.get('error', None)
    print(error)
    if error is not None:
        return Response({'message': 'access token을 가져올수 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    access_token = access_token_json.get('access_token')
    refresh_token = access_token_json.get('refresh_token')

    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
    }
    return Response({'message': '토큰 갱신 성공', **data}, status=status.HTTP_200_OK)


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
