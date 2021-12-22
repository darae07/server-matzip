from django.db.models import Subquery, OuterRef, Q, F, Prefetch
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import ReviewImage, Review, Comment
from group.models import TeamMember
from rest_framework import viewsets, status, pagination
from .serializer import ReviewImageSerializer, ReviewSerializer, ReviewListSerializer,\
    ReviewRetrieveSerializer ,CommentSerializer, CommentListSerializer
from django.contrib.gis.geos import Point


# Create your views here.
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = {
        'list': ReviewListSerializer,
        'retrieve': ReviewRetrieveSerializer
    }
    pagination_class = PageNumberPagination
    pagination_class.page_size = 5
    ordering = ['-created_at']
    company = None

    def get_serializer_context(self):
        context = super(ReviewViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class['list']
        if self.action == 'retrieve':
            return self.serializer_class['retrieve']

    def get_queryset(self):
        queryset = Review.objects.all().order_by('-created_at')
        return queryset

    def list(self, request):
        queryset = self.get_queryset()

        # 같은 팀 멤버이거나, 공개설정된 리뷰만 조회 가능
        team = self.request.query_params.get('team')
        if team:
            team_member = TeamMember.objects.filter(team=team)
            team_member_user_id = team_member.values('user')
            # queryset = queryset.prefetch_related(Prefetch('user__team_membership',
            #                                               queryset=team_member,
            #                                               to_attr='team_member'))

            queryset = queryset.filter(Q(public=True) | Q(user__in=team_member_user_id))
        else:
            queryset = queryset.filter(Q(public=True))
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        data['user'] = request.user.id
        lon = request.data['lon']
        lat = request.data['lat']

        if lon and lat:
            data['location'] = Point(float(lon), float(lat))
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

    def get_serializer_context(self):
        context = super(CommentViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        queryset = Comment.objects.filter(parent_comment=None).order_by('-created_at')
        return queryset

    def list(self, request):
        queryset = self.queryset
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

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

