from django.urls import path
from . import views
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from stores.views import StoreViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register(r'store', StoreViewSet)
router.register(r'category', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
