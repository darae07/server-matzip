from django.urls import path
from . import views
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from stores.views import StoreViewSet, DongViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register(r'stores', StoreViewSet)
router.register(r'dongs', DongViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
