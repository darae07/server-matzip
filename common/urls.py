from django.urls import path, include
from rest_framework import routers
from .views import CommonUserViewSet

router = routers.DefaultRouter()
router.register(r'user', CommonUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]