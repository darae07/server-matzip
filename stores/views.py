from django.shortcuts import render
from django.http import HttpResponse
from .models import Store, Menu, Category
from django.views import generic
from rest_framework import viewsets
from .serializer import StoreSerializer, CategorySerializer, MenuSerializer
from rest_framework.filters import SearchFilter


# Create your views here.
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer

    filter_backends = [SearchFilter]
    search_fields = 'name'

    def get_queryset(self):
        queryset = Store.objects.all()
        name = self.request.query_params.get('name')
        category = self.request.query_params.get('category')
        dong = self.request.query_params.get('dong')
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        if category is not None:
            queryset = queryset.filter(category=category)
        if dong is not None:
            queryset = queryset.filter(location__contains=dong)
        return queryset


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def create(self, request):
        store_menus = Menu.objects.filter(store=request.data['store'])