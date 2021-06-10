from django.shortcuts import render
from django.http import HttpResponse
from .models import Store, Dong, Menu, Category
from django.views import generic
from rest_framework import viewsets
from .serializer import StoreSerializer, DongSerializer, CategorySerializer


# Create your views here.
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class DongViewSet(viewsets.ModelViewSet):
    queryset = Dong.objects.all()
    serializer_class = DongSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer