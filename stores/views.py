from django.shortcuts import render
from django.http import HttpResponse
from .models import Store, Menu, Category
from django.views import generic
from rest_framework import viewsets
from .serializer import StoreSerializer, CategorySerializer


# Create your views here.
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer