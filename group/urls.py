from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views import CompanyViewSet

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]