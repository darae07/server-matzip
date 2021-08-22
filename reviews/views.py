from django.db.models import Subquery, OuterRef, Q
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from group.models import Contract, Company
from .models import ReviewImage, Review, Comment
from common.models import CommonUser
from rest_framework import viewsets, status, pagination
from .serializer import ReviewImageSerializer, ReviewSerializer, ReviewListSerializer,\
    CommentSerializer, CommentListSerializer


# Create your views here.
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewListSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5
    ordering = ['-created_at']
    company = None

    def get_queryset(self):
        # 같은 회사 멤버이거나, 공개설정된 리뷰만 조회 가능
        queryset = Review.objects.all().order_by('-created_at')

        # is user joined company?
        user = self.request.user
        company = self.request.query_params.get('company')
        if company:
            queryset = queryset.filter(Q(public=True) | Q(user__contract__company=company))
        else:
            queryset = queryset.filter(public=True)

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        store = request.query_params.get('store')

        if store:
            queryset = queryset.filter(store=store)

        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        serializer = ReviewSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        instance = Review.objects.get(pk=pk)
        data = request.data
        data['user'] = request.user.id
        serializer = ReviewSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ReviewImageViewSet(viewsets.ModelViewSet):
    queryset = ReviewImage.objects.all()
    serializer_class = ReviewImageSerializer
    parser_classes = [MultiPartParser]

    def create(self, request, *args, **kwargs):
        if request.FILES:
            request.data.image = request.FILES
        if request.data['review']:
            request.data.review = request.data['review']
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        if request.FILES:
            request.data.image = request.FILES
        if request.data['review']:
            request.data.review = request.data['review']
        instance = ReviewImage.objects.get(pk=pk)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer

    def get_queryset(self):
        queryset = Comment.objects.filter(parent_comment=None).order_by('-created_at')
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializer = CommentSerializer(data={**data, 'user': request.user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data
        comment = Comment.objects.get(pk=pk)
        serializer = CommentSerializer(comment, data={**data, 'user': request.user.id}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

