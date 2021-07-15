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
from rest_framework.pagination import PageNumberPagination


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

    paginator = PageNumberPagination()
    paginator.page_size = 10
    result_page = paginator.paginate_queryset(near_stores, request)
    serializer = StoreSerializer(result_page, many=True)
    print(result_page)
    return paginator.get_paginated_response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

    def create(self, request):
        print(request.data)
        store = request.data['store']
        name = request.data['name']
        same_menu = Menu.objects.filter(name=name, store=store)
        print(same_menu)
        if same_menu:
            return Response('same menu is exist', status=406)
        serializer = MenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data)


# 맛집 리스트 뷰
# 1. 검색조건 >
#    이름, 카테고리, 동, 근처(company, location),
# 2. 거리 > 근처일시 활성화
#    내위치 있는 경우 -> 내위치로 계산
#    회사 정보 있는 경우 -> 회사 위치로 계산
@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def store_list(request):
    queryset = Store.objects.all().order_by('id')

    name = request.query_params.get('name')
    category = request.query_params.get('category')
    dong = request.query_params.get('dong')
    near = request.query_params.get('near')
    order = request.query_params.get('ordering')

    if name is not None:
        queryset = queryset.filter(name__contains=name)
    if category is not None:
        queryset = queryset.filter(category=category)
    if dong is not None:
        queryset = queryset.filter(location__contains=dong)
    if near == 'company' or near == 'location':
        position = (0, 0)
        if near == 'company':
            user = request.user
            contract = Contract.objects.filter(user_id=user).first()
            if not contract:
                queryset = queryset.none()
            else:
                company_id = contract.company_id
                company = Company.objects.get(pk=company_id)
                if company.lat is None or company.lon is None:
                    queryset = queryset.none()
                else:
                    position = (company.lat, company.lon)
                    condition = get_condition(position)
                    queryset = queryset.filter(condition)
        if near == 'location':
            lat = request.query_params.get('lat')
            lon = request.query_params.get('lon')
            if lat is None or lon is None:
                queryset = queryset.none()
            else:
                lat, lon = float(lat), float(lon)
                position = (lat, lon)
                condition = get_condition(position)
                queryset = queryset.filter(condition)

        near_stores = []
        for store in queryset:
            distance = haversine(position, (store.lat, store.lon), unit='m')
            if distance > 1000:
                return
            store.distance = distance
            near_stores.append(store)
        queryset = near_stores

    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginator.ordering = 'id'
    if order is not None:
        if order == 'star':
            queryset = queryset.order_by('star')
        if order == 'distance':
            queryset = queryset.order_by('distance')
    result_page = paginator.paginate_queryset(queryset, request)
    serializer = StoreSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


def get_condition(position):
    return (
            Q(lat__range=(position[0] - 0.005, position[0] + 0.005)) |
            Q(lon__range=(position[1] - 0.007, position[1] + 0.007))
    )
