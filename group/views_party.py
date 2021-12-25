# party
# list - 나의 회사, 나의 파티 목록 투표 포함 조회
# retrieve - 나의 파티 투표 포함 조회

# membership
# r - 나의 초대 파디 목록
# c - 유저 - 파티 동일한 항목은 유일해야함

# vote
# r - 파티별 투표 조회
# c -
from django.db.models import Prefetch
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Party, Membership, Vote, Tag, TeamMember
from common.models import CommonUser
from rest_framework import viewsets, status
from .serializer import PartySerializer, PartyListSerializer, MembershipSerializer, VoteSerializer, \
    MembershipCreateSerializer, VoteListSerializer, TagCreateSerializer, TagSerializer
from matzip.handler import request_data_handler


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        # company = self.request.query_params.get('company')
        #
        # user = CommonUser.objects.prefetch_related(Prefetch('contract',
        #                                                     queryset=Contract.objects.filter(company=company)))
        # membership = Membership.objects.prefetch_related(Prefetch('user', queryset=user,
        #                                                           to_attr='prefetched_contracts'))
        # return queryset.prefetch_related(Prefetch('membership', queryset=membership, to_attr='prefetched_membership'))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('id')
        team = self.request.query_params.get('team')
        if team:
            queryset = queryset.filter(team=team)
        page = self.paginate_queryset(queryset)
        serializer = PartyListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        party = get_object_or_404(self.queryset, pk=pk)
        serializer = PartyListSerializer(party)
        return Response(serializer.data)


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
        team_member = TeamMember.objects.get(user=user, team=party.team)
        data['team_member'] = team_member.pk

        same_tag = Tag.objects.filter(team_member=data['team_member'], party=data['party'], review=data['review'])
        if same_tag:
            return Response({'message': '동일한 태그가 이미 존재합니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = TagCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
