from django.urls import path
from . import views
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from stores.views import StoreViewSet, CategoryViewSet, near_my_company, store_list, MenuViewSet

router = routers.DefaultRouter()
router.register(r'store', StoreViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'menu', MenuViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # path('near-my-company', near_my_company),
    # path('store-list', store_list),
]
