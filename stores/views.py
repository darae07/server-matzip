from django.shortcuts import render
from django.http import HttpResponse
from .models import Store, Menu, Category
from django.views import generic
from rest_framework import viewsets
from .serializer import StoreSerializer, CategorySerializer
from rest_framework.filters import SearchFilter


# Create your views here.
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    filter_backends = [SearchFilter]
    search_fields = 'name'


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
