from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.models_team import TeamMember
from matzip.handler import request_data_handler
from reviews.models import Review, ReviewImage
from reviews.serializers.review import ReviewListSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    ordering = ['-created_at']
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['POST'], parser_classes=[MultiPartParser, FormParser])
    def review(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['keyword'], ['content'])
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        review = Review.objects.create(keyword=data['keyword'], content=data['content'], team_member=team_member.id)
        if request.FILES:
            for image in request.FILES.getlist('image'):
                review_image = ReviewImage.objects.create(review=review.id, image=image)
        serializer = ReviewListSerializer(review)
        return Response({'message': '리뷰를 작성했습니다.', **serializer.data}, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        keyword = request.query_params.get('keyword')
        if keyword:
            queryset = queryset.filter(keyword=keyword)
        page = self.paginate_queryset(queryset.order_by('-created_at'))
        serializer = ReviewListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)
