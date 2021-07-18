from django.db.models import F, Prefetch, OuterRef, Subquery
from rest_framework import viewsets
from .models import CommonUser
from .serializers import UserSerializer
from group.models import Contract


class CommonUserViewSet(viewsets.ModelViewSet):
    queryset = CommonUser.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        queryset = CommonUser.objects.prefetch_related(Prefetch('contract', queryset=Contract.objects.all()))
        return queryset
