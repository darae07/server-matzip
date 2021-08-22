from django.db.models import Prefetch
from rest_framework import viewsets
from .models import CommonUser
from .costume_serializers import FullUserSerializer
from group.models import Contract
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.conf import settings


class CommonUserViewSet(viewsets.ModelViewSet):
    queryset = CommonUser.objects.all()
    serializer_class = FullUserSerializer

    def get_queryset(self):
        company = self.request.query_params.get('company')
        queryset = CommonUser.objects.prefetch_related(
            Prefetch('contract', queryset=Contract.objects.filter(company=company))).order_by('-date_joined')

        return queryset


class GoogleLogin(SocialLoginView):
    authentication_classes = []
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000"
    client_class = OAuth2Client