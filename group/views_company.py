# company
# r - 나의 회사 목록

# contract
# r - 나의 계약 목록
# c - 회사 - 유저 동일한 항목은 유일해야함

# invite
# r - 나의 초대 목록
# c - 회사 - 유저 동일한 항목은 유일해야함
from rest_framework.response import Response
from .models import Company, Contract, Invite
from rest_framework import viewsets, status
from .serializer import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_queryset(self):
        user = self.request.user
        contracts = Contract.objects.filter(user=user).values('company')
        queryset = self.queryset.filter(company__in=contracts)
        return queryset
