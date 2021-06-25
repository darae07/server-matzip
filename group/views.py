from django.shortcuts import render
from .models import Company
from rest_framework import viewsets
from .serializer import CompanySerializer, CompanyMemberSerializer
from common.models import CommonUser


# Create your views here.
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CompanyMemberViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanyMemberSerializer
