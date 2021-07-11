from django.urls import path
from django.conf.urls import url, include
from rest_framework import routers
from reviews.views import ReviewViewSet, CommentViewSet, ReviewImageViewSet

router = routers.DefaultRouter()
router.register(r'review', ReviewViewSet)
router.register(r'comment', CommentViewSet)
router.register(r'image', ReviewImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]