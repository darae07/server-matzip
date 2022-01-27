from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from reviews.view import CommentViewSet, ReviewImageViewSet, LikeViewSet
from .views.review import ReviewViewSet

router = routers.DefaultRouter()
router.register(r'review', ReviewViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'image', ReviewImageViewSet)
router.register(r'like', LikeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]