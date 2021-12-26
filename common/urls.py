from django.urls import path, include
from rest_framework import routers
from .views import CommonUserViewSet, kakao_login, kakao_login_callback

router = routers.DefaultRouter()
router.register(r'user', CommonUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('kakao-login/', kakao_login),
    path('kakao-callback/', kakao_login_callback),
]