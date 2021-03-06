from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from group.models_team import TeamMember
from matzip.handler import request_data_handler
from reviews.models import Review
from reviews.serializers.review import ReviewListSerializer, ReviewMemberListSerializer
from stores.models import Keyword, Category
from stores.serializers.keword import KeywordSerializer, KeywordCreateSerializer


class KeywordViewSet(viewsets.ModelViewSet):
    queryset = Keyword.objects.all()
    serializer_class = KeywordSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('-hit_count')
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        keyword = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(keyword)
        return Response({**serializer.data, 'message': '키워드를 조회했습니다.'}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        team = team_member.team
        data = request_data_handler(request.data, ['name'], ['category'])

        category = Category.objects.get(id=data['category'])
        keyword = Keyword.objects.hit_keyword(name=data['name'], team=team, category=category)
        serializer = self.serializer_class(keyword)
        return Response({**serializer.data, 'message': '키워드를 등록했습니다.'})

    @action(detail=True, methods=['GET'])
    def reviews(self, request, pk=None):
        keyword = get_object_or_404(self.queryset, pk=pk)
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if keyword.team.id != team_member.team.id:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = Review.objects.filter(keyword=pk, content__isnull=False).order_by('-created_at')
        page = self.paginate_queryset(queryset)
        serializer = ReviewListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['GET'])
    def review_members(self, request, pk=None):
        keyword = get_object_or_404(self.queryset, pk=pk)
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if keyword.team.id != team_member.team.id:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = Review.objects.filter(keyword=pk).order_by('-created_at')
        serializer = ReviewMemberListSerializer(queryset, many=True)
        return Response({'message': '리뷰 멤버 목록을 불러왔습니다.', 'results': serializer.data, 'count': queryset.count()},
                        status=status.HTTP_200_OK)
