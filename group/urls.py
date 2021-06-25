from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import CompanyViewSet, CompanyMemberViewSet

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet)
router.register(r'company-member', CompanyMemberViewSet)

urlpatterns = [
    path('', include(router.urls)),
]