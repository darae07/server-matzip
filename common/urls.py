from django.urls import path, include
from rest_framework import routers
from .views import CommonUserViewSet, kakao_login, kakao_login_callback, LoginView
from dj_rest_auth.views import LogoutView
from dj_rest_auth.registration.views import RegisterView

router = routers.DefaultRouter()
router.register(r'user', CommonUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('kakao-login/', kakao_login),
    path('kakao-callback/', kakao_login_callback),
    path('login/', LoginView.as_view(), name='rest_login'),
    path('logout/', LogoutView.as_view(), name='rest_logout'),
    path('registration/', RegisterView.as_view(), name='rest_register'),
]