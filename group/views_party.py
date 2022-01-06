# party
# list - 나의 회사, 나의 파티 목록 투표 포함 조회
# retrieve - 나의 파티 투표 포함 조회

# membership
# r - 나의 초대 파디 목록
# c - 유저 - 파티 동일한 항목은 유일해야함

# vote
# r - 파티별 투표 조회
# c -
from django.db.models import Prefetch, F
from django.utils.dateparse import parse_datetime
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Party, Membership, Vote, Tag, TeamMember, Team
from common.models import CommonUser
from rest_framework import viewsets, status
from .serializer import PartySerializer, PartyListSerializer, MembershipSerializer, VoteSerializer, \
    MembershipCreateSerializer, VoteListSerializer, TagCreateSerializer, TagSerializer, PartyDetailSerializer
from matzip.handler import request_data_handler
import datetime


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = {
        'create': PartySerializer,
        'list': PartyListSerializer,
        'retrieve': PartyDetailSerializer
    }
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.order_by(F('closed_at').desc(nulls_first=True), '-created_at')
        return queryset

    def get_serializer_context(self):
        context = super(PartyViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return self.serializer_class['create']
        if self.action == 'retrieve':
            return self.serializer_class['retrieve']
        return self.serializer_class['list']

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('id')
        team = self.request.query_params.get('team')
        if team:
            queryset = queryset.filter(team=team)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        party = get_object_or_404(self.queryset, pk=pk)
        serializer = self.get_serializer(party)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['name', 'team'], ['description', 'date'])
        if Party.objects.filter(team=data['team'], name=data['name']):
            return Response({'message': '이미 같은 파티가 있습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if data['date']:
            data['date'] = parse_datetime(data['date'])
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            party = Party.objects.get(pk=pk)
            if 'date' in data:
                data['date'] = parse_datetime(data['date'])
            serializer = self.get_serializer(instance=party, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data={**serializer.data, 'message': '파티가 업데이트 되었습니다.'}, status=status.HTTP_200_OK)
        except Party.DoesNotExist:
            return Response({'message': '파티를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def close(self, request, pk=None):
        try:
            party = Party.objects.get(pk=pk)
            now = datetime.datetime.now()
            party.closed_at = now
            party.save()
            serializer = PartySerializer(party)
            return Response(data={**serializer.data, 'message': '파티가 종료되었습니다.'}, status=status.HTTP_200_OK)
        except Party.DoesNotExist:
            return Response({'message': '파티를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset

        # company = self.request.query_params.get('company')
        state = self.request.query_params.get('state')
        # if company:
        #     queryset = queryset.filter(user__contract__company=company)
        if state:
            queryset = queryset.filter(status=state)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        page = self.paginate_queryset(queryset)
        serializer = MembershipSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        membership = get_object_or_404(self.queryset, pk=pk)
        serializer = MembershipSerializer(membership)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data
        party = data['party']
        user = data['user']

        same_membership = Membership.objects.filter(team_member__user=user, party=party)
        if same_membership:
            return Response({'message': 'the same membership exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = MembershipCreateSerializer(data=data)

        if serializer.is_valid():
            membership = Membership.objects.create(**serializer.validated_data)
            membership.save()
            return Response({'id': membership.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        instance = Membership.objects.get(pk=pk)
        serializer = MembershipCreateSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
