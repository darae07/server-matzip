from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from stores.views.views import StoreViewSet, CategoryViewSet, MenuViewSet
from stores.views.keyword import KeywordViewSet

router = routers.DefaultRouter()
router.register(r'store', StoreViewSet)
router.register(r'category', CategoryViewSet)
router.register(r'menu', MenuViewSet)
router.register(r'keyword', KeywordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
