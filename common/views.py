from django.db.models import Prefetch
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, request, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CommonUser
from .costume_serializers import FullUserSerializer
from .serializers import UserSerializer
from group.models import Contract
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings
from rest_framework.parsers import MultiPartParser


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
        if self.request.FILES:
            data.image = self.request.FILES
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


class GoogleLogin(SocialLoginView):
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000"
    client_class = OAuth2Client


@csrf_exempt
def google_token():
    if 'code' not in request.body.decode():
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
