from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Store, Menu, Category
from group.models import Contract, Company
from rest_framework import viewsets, permissions
from .serializer import StoreSerializer, CategorySerializer, MenuSerializer
from rest_framework.filters import SearchFilter
from haversine import haversine


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
