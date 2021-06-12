from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from reviews.views import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'review', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]