# company
# r - 나의 회사 목록

# contract
# r - 나의 계약 목록
# c - 회사 - 유저 동일한 항목은 유일해야함

# invite
# r - 나의 초대 목록
# c - 회사 - 유저 동일한 항목은 유일해야함
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Company, Contract, Invite
from rest_framework import viewsets, status
from .serializer import CompanySerializer, ContractSerializer, InviteSerializer, InviteCreateSerializer
from django.db.models import Q, Prefetch
from common.models import CommonUser
from common.costume_serializers import FullUserSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        user = self.request.user
        contracts = Contract.objects.filter(user=user).values('company')
        queryset = self.queryset.filter(company__in=contracts)
        return queryset

    @action(detail=True)
    def members(self, request, pk=None):
        contract = Contract.objects.filter(company=pk)
        print(contract)
        members = CommonUser.objects.filter(contract__company=pk)\
            .prefetch_related(Prefetch(lookup='contract', queryset=Contract.objects.filter(company=pk),
                                       to_attr='prefetched_contract'))
        page = self.paginate_queryset(members)
        if page is not None:
            serializer = FullUserSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = FullUserSerializer(members, many=True)
        return Response(serializer.data)


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


class InviteViewSet(viewsets.ModelViewSet):
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(receiver=user)
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        data['sender'] = user.id

        same_contract = Contract.objects.filter(Q(user=data['receiver']) & Q(company=data['company']))
        if same_contract:
            return Response({'message': 'the same contract exists'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        same_invite = Invite.objects.filter(Q(receiver=data['receiver']) & Q(company=data['company']))
        if same_invite:
            return Response({'message': 'the same invite exists'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = InviteCreateSerializer(data=data)
        if serializer.is_valid():
            invite = Invite.objects.create(**serializer.validated_data)
            invite.save()
            print(serializer.data)
            return Response({ 'id': invite.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
