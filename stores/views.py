from django.shortcuts import render
from django.http import HttpResponse
from .models import Store, Dong, Menu, Category
from django.views import generic


# Create your views here.
class StoreList(generic.ListView):
    def get_queryset(self):
        return Store.objects.order_by('id')


def index(request):
    store_list = Store.objects.order_by('id')
    context = {
        'stores': store_list,
    }
    return HttpResponse(context)


class StoreDetail(generic.DetailView):
    model = Store
