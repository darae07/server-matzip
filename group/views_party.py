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
from rest_framework.response import Response
from .models import Party, Membership, Vote, Contract
from common.models import CommonUser
from rest_framework import viewsets, status
from .serializer import PartySerializer, PartyListSerializer, MembershipSerializer, VoteSerializer, \
    MembershipCreateSerializer


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

    def get_queryset(self):
        queryset = self.queryset
        company = self.request.query_params.get('company')

        user = CommonUser.objects.prefetch_related(Prefetch('contract',
                                                            queryset=Contract.objects.filter(company=company)))
        membership = Membership.objects.prefetch_related(Prefetch('user', queryset=user,
                                                                  to_attr='prefetched_contracts'))
        return queryset.prefetch_related(Prefetch('membership', queryset=membership, to_attr='prefetched_membership'))

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        page = self.paginate_queryset(queryset)
        serializer = PartyListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        party = get_object_or_404(self.queryset, pk=pk)
        serializer = PartyListSerializer(party)
        return Response(serializer.data)


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(user=user)

        company = self.request.query_params.get('company')
        state = self.request.query_params.get('state')
        if company:
            queryset = queryset.filter(user__contract__company=company)
        if state:
            queryset = queryset.filter(status=state)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        party = data['party']
        user = data['user']

        same_membership = Membership.objects.filter(user=user, party=party)
        if same_membership:
            return Response({'message': 'the same membership exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = MembershipCreateSerializer(data=data)

        if serializer.is_valid():
            membership = Membership.objects.create(**serializer.validated_data)
            membership.save()
            return Response({'id': membership.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def get_queryset(self):
        queryset = self.queryset
        party = self.request.query_params.get('party')
        if party:
            queryset = queryset.filter(membership__party=party)
        return queryset
