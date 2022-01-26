# party
# list - 나의 회사, 나의 파티 목록 투표 포함 조회
# retrieve - 나의 파티 투표 포함 조회

# membership
# r - 나의 초대 파디 목록
# c - 유저 - 파티 동일한 항목은 유일해야함

# vote
# r - 파티별 투표 조회
# c -
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models_crew import Vote
from .models_party import Party
from .models_team import Tag, TeamMember, Team
from rest_framework import viewsets, status
from .serializer import VoteSerializer, \
    VoteListSerializer, TagCreateSerializer, TagSerializer
from matzip.handler import request_data_handler


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        party = self.request.query_params.get('party')
        if party:
            queryset = queryset.filter(membership__party=party)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        page = self.paginate_queryset(queryset)
        serializer = VoteListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        vote = get_object_or_404(self.queryset, pk=pk)
        serializer = VoteListSerializer(vote)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request_data_handler(request.data, ['party', 'tag'])
        party = data['party']
        tag = data['tag']

        try:
            party_instance = Party.objects.get(id=party)
        except Party.DoesNotExist:
            return Response({'message': '파티를 찾을수 없습니다'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            team_instance = Team.objects.get(id=party_instance.team.id)
        except Team.DoesNotExist:
            return Response({'message': '팀을 찾을수 없습니다'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            team_member_instance = TeamMember.objects.get(team=team_instance.id, user=user.id)
        except TeamMember.DoesNotExist:
            return Response({'message': '멤버를 찾을수 없습니다'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data['team_member'] = team_member_instance.id

        if Vote.objects.filter(party=party, tag=tag, team_member=team_member_instance.id):
            return Response({'message': '동일한 투표가 이미 존재합니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = VoteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = VoteSerializer(instance=serializer.instance)
        return Response(data={**serializer.data, 'message': '투표가 생성되었습니다.'}, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        party = self.request.query_params.get('party')
        if party:
            queryset = queryset.filter(party=party)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        data = request_data_handler(request.data, ['party', 'review'])
        party = Party.objects.get(pk=data['party'])
        try:
            team_member = TeamMember.objects.get(user=user, team=party.team)
        except TeamMember.DoesNotExist:
            return Response({'message': '멤버를 찾을수 없습니다'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data['team_member'] = team_member.pk

        same_tag = Tag.objects.filter(team_member=data['team_member'], party=data['party'], review=data['review'])
        if same_tag:
            return Response({'message': '동일한 태그가 이미 존재합니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = TagCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = TagCreateSerializer(instance=serializer.instance)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
