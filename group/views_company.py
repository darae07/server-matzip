# company
# r - 나의 회사 목록
# r - 나의 회사 멤버 조회

# contract
# r - 나의 계약 목록
# c - 회사 - 유저 동일한 항목은 유일해야함

# invite -> 파티 초대로 변경
# r - 나의 초대 목록
# c - 파티 - 유저 동일한 항목은 유일해야함
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Company, Contract, Invite, Party
from rest_framework import viewsets, status
from .serializer import CompanySerializer, ContractSerializer, InviteSerializer, InviteCreateSerializer, MembershipCreateSerializer
from django.db.models import Q, Prefetch
from common.models import CommonUser
from common.costume_serializers import FullUserSerializer
from django.contrib.gis.geos import Point
from rest_framework.exceptions import APIException
from .constants import InviteStatus


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        user = self.request.user
        contracts = Contract.objects.filter(user=user.id).values('company')
        queryset = self.queryset.filter(id__in=contracts)
        return queryset

    @action(detail=True)
    def members(self, request, pk=None):
        members = CommonUser.objects.filter(contract__company=pk) \
            .prefetch_related(Prefetch(lookup='contract', queryset=Contract.objects.filter(company=pk),
                                       to_attr='prefetched_contract'))
        page = self.paginate_queryset(members)
        if page is not None:
            serializer = FullUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FullUserSerializer(members, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data

        lon = request.data['lon']
        lat = request.data['lat']

        if lon and lat:
            data['location'] = Point(float(lon), float(lat))

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            company = Company.objects.create(**serializer.validated_data)
            company.save()
            return Response({'id': company.pk, 'name': company.name}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        lon = request.data['lon']
        lat = request.data['lat']

        company = Company.objects.get(pk=pk)
        if lon and lat:
            data['location'] = Point(float(lon), float(lat))

        serializer = self.serializer_class(company, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response({'id': pk}, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = Contract.objects.all()
    serializer_class = ContractSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        user = data['user']

        same_contract = Contract.objects.filter(Q(user=user) & Q(company=data['company']))
        if same_contract:
            return Response({'message': 'the same contract exists'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            contract = Contract.objects.create(**serializer.validated_data)
            print(contract)
            contract.save()
            return Response({'id': contract.pk, 'user': contract.user.id, 'username': contract.user.username},
                            status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)


# 파티 초대 기능
class InviteViewSet(viewsets.ModelViewSet):
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(receiver__user=user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        print(data)

        same_invite = Invite.objects.filter(Q(receiver=data['receiver']) & Q(party=data['party']))
        if same_invite:
            return Response({'message': '이미 초대된 회원입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)

        data['party_id'] = data['party']
        serializer = InviteCreateSerializer(data=data)
        if serializer.is_valid():
            invite = Invite.objects.create(**serializer.validated_data)
            invite.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        instance = self.get_object()
        if instance.status == InviteStatus.ACCEPTED.value:
            return Response({'message': '이미 승인된 초대입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        membership = MembershipCreateSerializer(data={'team_member': instance.receiver.id, 'party': instance.party.id})
        if membership.is_valid():
            membership.save()
            instance.status = InviteStatus.ACCEPTED.value
            instance.save()
            return Response(membership.data, status=status.HTTP_200_OK)
        return Response(membership.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data
        invite = Invite.objects.get(pk=pk)
        serializer = self.serializer_class(invite, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

