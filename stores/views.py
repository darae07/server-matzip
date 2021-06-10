from django.shortcuts import render
from django.http import HttpResponse
from .models import Store, Dong, Menu, Category
from django.views import generic
from rest_framework import viewsets
from .serializer import StoreSerializer


# Create your views here.
class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer


def index(request):
    store_list = Store.objects.order_by('id')
    context = {
        'stores': store_list,
    }
    return HttpResponse(context)


class StoreDetail(generic.DetailView):
    model = Store
