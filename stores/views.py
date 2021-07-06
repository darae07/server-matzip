from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Store, Menu, Category
from group.models import Contract, Company
from rest_framework import viewsets, permissions
from .serializer import StoreSerializer, CategorySerializer, MenuSerializer
from rest_framework.filters import SearchFilter
from haversine import haversine
from django.db import models


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
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        near = self.request.query_params.get('near')
        user = self.request.user
        print(user, near)

        if user and near == 'true':
            contract = Contract.objects.filter(user_id=user).first()
            if contract:
                company_id = contract.company_id
                company = Company.objects.get(pk=company_id)
                position = (company.lat, company.lon)
                print(position)
                condition = (
                        Q(lat__range=(company.lat - 0.005, company.lat + 0.005)) |
                        Q(lon__range=(company.lon - 0.007, company.lon + 0.007))
                )
                queryset = queryset.filter(condition)
                near_store_ids = []
                near_store_distances = []
                for store in queryset:
                    distance = haversine(position, (store.lat, store.lon), unit='m')
                    if distance <= 1000:
                        near_store_ids.append(store.id)
                        near_store_distances.append(distance)
                # near_store_ids = [store.id for store in queryset
                #                   if haversine(position, (store.lat, store.lon)) <= 2]
                queryset = queryset.filter(id__in=near_store_ids)
                # queryset = queryset.annotate(distance=haversine(position, ('lat', 'lon'), unit='m'))
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        if category is not None:
            queryset = queryset.filter(category=category)
        if dong is not None:
            queryset = queryset.filter(location__contains=dong)
        if lat is not None and lon is not None:
            lat, lon = float(lat), float(lon)
            position = (lat, lon)

            condition = (
                    Q(lat__range=(lat - 0.005, lat + 0.005)) |
                    Q(lon__range=(lon - 0.007, lon + 0.007))
            )
            queryset = queryset.filter(condition)

            near_store_ids = [store.id for store in queryset
                              if haversine(position, (store.lat, store.lon)) <= 2]
            queryset = queryset.filter(id__in=near_store_ids)
        return queryset


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def near_my_company(request):
    user = request.user
    contract = Contract.objects.filter(user_id=user).first()
    if not contract:
        return Response('user`s company is not defined', status=204)
    company_id = contract.company_id

    company = Company.objects.get(pk=company_id)

    position = (company.lat, company.lon)
    condition = (
            Q(lat__range=(company.lat - 0.005, company.lat + 0.005)) |
            Q(lon__range=(company.lon - 0.007, company.lon + 0.007))
    )
    queryset = Store.objects.filter(condition)

    near_stores = [store for store in queryset
                   if haversine(position, (store.lat, store.lon)) <= 2]
    for store in near_stores:
        store.distance = haversine(position, (store.lat, store.lon), unit='m')
    serializer = StoreSerializer(near_stores, many=True)
    return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def create(self, request):
        store_menus = Menu.objects.filter(store=request.data['store'])
