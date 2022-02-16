import os
import requests
import rest_framework
from django.contrib import messages
from django.contrib.auth import login

from django.db.models import Prefetch
from django.shortcuts import redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, renderer_classes, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from matzip.handler import request_data_handler
from .models import CommonUser, ResetPasswordCode
from .costume_serializers import FullUserSerializer
from .serializers import UserSerializer
from group.models_team import Contract
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.sites.shortcuts import get_current_site
from dj_rest_auth import views
from dj_rest_auth.serializers import JWTSerializer
from matzip.smtp import send_plain_mail, send_multipart_mail
from .serializers import ResetPasswordCodeSerializer
from datetime import datetime

SITE_DOMAIN = os.environ.get('SITE_DOMAIN')
KAKAO_CLIENT_ID = os.environ.get('KAKAO_ID')
KAKAO_REDIRECT_URI = SITE_DOMAIN + '/api/common/kakao-callback/'
KAKAO_SECRET = os.environ.get('KAKAO_SECRET')
RESPONSE_TYPE = 'code'
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = SITE_DOMAIN + '/api/common/google-callback/'
GOOGLE_STATE = os.environ.get('GOOGLE_STATE')


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

    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
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
        return Response(data={**serializer.data, 'message': '회원 정보를 변경했습니다.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_profile_image(self, request, pk=None):
        user = self.request.user
        user.image.delete(save=True)
        user.save()
        return Response(data={'id': pk, 'message': '회원 프로필 이미지를 삭제했습니다.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser], permission_classes=[IsAuthenticated])
    def upload_profile_image(self, request, pk=None):
        user = self.request.user
        data = {}
        if request.FILES:
            data['image'] = request.FILES['image']
        serializer = UserSerializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data={**serializer.data, 'message': '회원 프로필 이지미를 등록했습니다.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def find_email(self, request):
        data = request_data_handler(request.data, ['nickname'])
        nickname = data['nickname']
        try:
            user = CommonUser.objects.get(nickname=nickname)
            serializer = UserSerializer(user)
            return Response(data={**serializer.data, 'message': '회원 정보를 조회했습니다.'}, status=status.HTTP_200_OK)
        except CommonUser.DoesNotExist:
            return Response({'message': '회원 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def send_reset_password_code(self, request):
        data = request_data_handler(request.data, ['email'])
        email = data['email']

        try:
            user = CommonUser.objects.get(email=email)
            serializer = ResetPasswordCodeSerializer(data={'user': user.id})
            serializer.is_valid(raise_exception=True)
            past_password_codes = ResetPasswordCode.objects.filter(user=user).update(status=ResetPasswordCode.EXPIRED)
            reset_password_code = ResetPasswordCode.objects.create(**serializer.validated_data)
            code = reset_password_code.code
            expired_at = reset_password_code.expired_at.strftime('%Y-%m-%d %H:%M')

            try:
                send_multipart_mail(email, '오늘뭐먹지 비밀번호 초기화 코드입니다.',
                                    {'plain': '',
                                     'html': f'<html>'
                                             f'<head></head>'
                                             f'<body>'
                                             f'<h1>오늘뭐먹지 비밀번호 초기화 코드입니다.</h1>'
                                             f'<p>코드: {code}</p>'
                                             f'<p>유효기간은 {expired_at}까지입니다. </p>'
                                             f'</body>'
                                             f'</html>'})
                return Response(data={'message': '메일을 전송했습니다.'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except CommonUser.DoesNotExist:
            return Response({'message': '회원 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def confirm_password_reset_code(self, request):
        data = request_data_handler(request.data, ['email', 'code'])
        code = data['code']
        email = data['email']

        try:
            user = CommonUser.objects.get(email=email)
            try:
                reset_password_code = ResetPasswordCode.objects.get(user=user, code=code)
                if reset_password_code.status == ResetPasswordCode.USED:
                    return Response({'message': '사용된 인증코드입니다. 다시 발급해 주세요.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                if reset_password_code.status == ResetPasswordCode.EXPIRED:
                    return Response({'message': '만료된 인증코드입니다. 유효한 코드를 이용하거나 다시 발급해 주세요.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
                if reset_password_code.expired_at < datetime.now():
                    return Response({'message': '유효시간이 경과되었습니다. 다시 발급해 주세요.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

                if reset_password_code.status == ResetPasswordCode.ACTIVE:
                    reset_password_code.status = ResetPasswordCode.USED
                    reset_password_code.save()
                    return Response({'message': '인증코드 확인이 완료되었습니다.', 'user': user.id})

            except ResetPasswordCode.DoesNotExist:
                return Response({'message': '인증코드를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except CommonUser.DoesNotExist:
            return Response({'message': '회원 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password_by_code(self, request):
        data = request_data_handler(request.data, ['user', 'code', 'password'])
        user_id = data['user']
        code = data['code']
        password = data['password']

        try:
            user = CommonUser.objects.get(id=user_id)
            try:
                reset_code = ResetPasswordCode.objects.get(user=user_id, code=code, status=ResetPasswordCode.USED)
                user.set_password(password)
                user.save()
                reset_code.status = ResetPasswordCode.EXPIRED
                reset_code.save()
                return Response({'message': '비밀번호 변경이 완료되었습니다.', 'user': user.id})
            except ResetPasswordCode.DoesNotExist:
                return Response({'message': '확인된 인증코드를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except CommonUser.DoesNotExist:
            return Response({'message': '회원 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)


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


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def google_login(request):
    try:
        scope = 'https://www.googleapis.com/auth/userinfo.email'
        return redirect(
            f'https://accounts.google.com/o/oauth2/v2/auth?client_id={GOOGLE_CLIENT_ID}&response_type=code&'
            f'redirect_uri={GOOGLE_REDIRECT_URI}&scope={scope}'
        )
    except Exception as e:
        print(e)
        messages.error(request, e)
        return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(('GET',))
@renderer_classes((JSONRenderer,))
def google_login_callback(request):
    try:
        code = request.GET.get('code', None)
        if code is None:
            TokenException('코드를 불러올 수 없습니다.')
        token_request = requests.post(
            f'https://oauth2.googleapis.com/token?client_id={GOOGLE_CLIENT_ID}&client_secret={GOOGLE_CLIENT_SECRET}'
            f'&code={code}&grant_type=authorization_code&redirect_uri={GOOGLE_REDIRECT_URI}&state={GOOGLE_STATE}'
        )
        token_request_json = token_request.json()
        error = token_request_json.get('error', None)
        if error is not None:
            TokenException('access token을 가져올수 없습니다.')
        access_token = token_request_json.get('access_token')
        email_request = requests.get(
            f'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}'
        )
        email_request_status = email_request.status_code
        if email_request_status != 200:
            TokenException('이메일을 가져올수 없습니다.')
        email_request_json = email_request.json()
        email = email_request_json.get('email')

        try:
            user = CommonUser.objects.get(email=email)
        except CommonUser.DoesNotExist:
            user = None
        if user is not None:
            if user.login_method != CommonUser.LOGIN_GOOGLE:
                AlertException(f'{user.login_method}로 로그인 해주세요')
        else:
            user = CommonUser(email=email, login_method=CommonUser.LOGIN_GOOGLE)
            user.set_unusable_password()
            user.save()
        messages.success(request, f'{user.email} 구글 로그인 성공')
        login(request, user, backend="django.contrib.auth.backends.ModelBackend",)
        data = {
            'user': user,
            'access_token': access_token,
            'refresh_token': None,
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
