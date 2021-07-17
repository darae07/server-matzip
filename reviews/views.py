from django.shortcuts import render
from rest_framework.response import Response

from .models import ReviewImage, Review, Comment
from rest_framework import viewsets, status, pagination
from .serializer import ReviewImageSerializer, ReviewSerializer, CommentSerializer


# Create your views here.
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination.PageNumberPagination.page_size = 5
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Review.objects.all().order_by('-created_at')
        return queryset


class ReviewImageViewSet(viewsets.ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

