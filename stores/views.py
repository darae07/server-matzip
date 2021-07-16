from django.db.models import OuterRef, Avg, Subquery
from rest_framework.response import Response
from .models import Store, Menu, Category
from group.models import Contract, Company
from reviews.models import Review
from rest_framework import viewsets
from .serializer import StoreSerializer, CategorySerializer, MenuSerializer
from rest_framework.filters import SearchFilter
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance
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
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('lon')
        near = self.request.query_params.get('near')
        order = self.request.query_params.get('order')
        user = self.request.user

        store_reviews = Review.objects.filter(store=OuterRef('pk')).order_by().values('store')
        avg_stars = store_reviews.annotate(avg_star=Avg('star')).values('avg_star')
        queryset = queryset.annotate(review_stars=Subquery(avg_stars))

        if name is not None:
            queryset = queryset.filter(name__contains=name)
        if category is not None:
            queryset = queryset.filter(category=category)
        if near is not None:
            if near == 'point' and lat and lon:
                ref_location = Point(lon, lat, srid=4326)
                queryset = queryset.filter(location__dwithin=(ref_location, 2000))\
                    .annotate(distance=GeometryDistance('location', ref_location))

            if near == 'company':
                contract = Contract.objects.filter(user_id=user).first()
                if not contract:
                    queryset = queryset.none()
                else:
                    company_id = contract.company_id
                    company = Company.objects.get(pk=company_id)
                    if company.location is None:
                        queryset = queryset.none()
                    else:
                        ref_location = company.location
                        queryset = queryset.filter(location__dwithin=(ref_location, 2000))\
                            .annotate(distance=GeometryDistance('location', ref_location))
        if order is not None:
            if order == 'review':
                queryset = queryset.order_by('review_stars')
            if order == 'distance' and near is not None:
                queryset = queryset.order_by('distance')

        return queryset


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

