from django.db.models import F, Prefetch, OuterRef, Subquery
from rest_framework import viewsets
from .models import CommonUser
from .costume_serializers import FullUserSerializer
from group.models import Contract


class CommonUserViewSet(viewsets.ModelViewSet):
    queryset = CommonUser.objects.all()
    serializer_class = FullUserSerializer

    def get_queryset(self):
        user = self.request.user
        my_contract = Contract.objects.filter(user=user).first()
        if my_contract:
            my_company = my_contract.company
            queryset = CommonUser.objects.prefetch_related(
                Prefetch('contract', queryset=Contract.objects.filter(company=my_company))).order_by('-date_joined')
        return queryset
