from django.db.models import OuterRef, Avg, Subquery, Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import Store, Menu, Category
from group.models import Contract, Company
from reviews.models import Review
from rest_framework import viewsets, pagination, status
from .serializer import StoreSerializer, CategorySerializer, MenuSerializer
from rest_framework.filters import SearchFilter
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import GeometryDistance
from django.contrib.gis.geos import Point


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size = 20

    filter_backends = [SearchFilter]
    search_fields = 'name'
    company = None
    
    def get_company(self):
        user = self.request.user
        company = self.request.query_params.get('company')
        # is user joined company?
        contract = Contract.objects.filter(Q(user_id=user) & Q(company=company)).first()
        if contract:
            company_id = contract.company_id
            self.company = Company.objects.get(pk=company_id)

    def get_review(self, queryset):
        # add review star score
        store_reviews = Review.objects.filter(store=OuterRef('pk')).values('store')
        avg_stars = store_reviews.annotate(avg_star=Avg('star')).values('avg_star')
        queryset = queryset.annotate(review_stars=Subquery(avg_stars))

        if self.company:
            company_members = Contract.objects.filter(company=self.company.id).values('user')
            members_store_reviews = store_reviews.filter(user__in=company_members)
            member_avg_stars = members_store_reviews.annotate(member_avg_star=Avg('star')).values('member_avg_star')
            queryset = queryset.annotate(members_stars=Subquery(member_avg_stars))
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = Store.objects.all()
        name = request.query_params.get('name')
        category = request.query_params.get('category')
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        near = request.query_params.get('near')
        order = request.query_params.get('order')

        self.get_company()

        if name is not None:
            queryset = queryset.filter(name__contains=name)
        if category is not None:
            queryset = queryset.filter(category=category)
        if near is not None:
            if near == 'point' and lat and lon:
                ref_location = Point(lon, lat, srid=4326)
                queryset = queryset.filter(location__dwithin=(ref_location, 2000)) \
                    .annotate(distance=GeometryDistance('location', ref_location))

            if near == 'company':
                if not self.company:
                    queryset = queryset.none()
                else:
                    if self.company.location is None:
                        queryset = queryset.none()
                    else:
                        ref_location = self.company.location
                        queryset = queryset.filter(location__dwithin=(ref_location, 2000)) \
                            .annotate(distance=GeometryDistance('location', ref_location))

        # add review star score
        queryset = self.get_review(queryset)

        if order is not None:
            if order == 'review':
                queryset = queryset.order_by('review_stars')
            if order == 'distance' and near is not None:
                queryset = queryset.order_by('distance')

        page = self.paginate_queryset(queryset)
        serializer = self.serializer_class(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        queryset = Store.objects.filter(pk=pk)
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        self.get_company()

        ref_location = None
        if self.company and self.company.location:
            ref_location = self.company.location
        if lat and lon:
            ref_location = Point(lon, lat, srid=4326)
        if ref_location:
            queryset = queryset.annotate(distance=GeometryDistance('location', ref_location))

        # add review star score
        queryset = self.get_review(queryset)

        store = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(store)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        data = request.data

        lon = request.data['lon']
        lat = request.data['lat']

        if lon and lat:
            data['location'] = Point(float(lon), float(lat))

            ref_location = Point(lon, lat, srid=4326)
            same_store = Store.objects.filter(name=request.data['name'], location__dwithin=(ref_location, 200))
            if same_store:
                return Response({'message': 'the same store exists'},
                                status=status.HTTP_406_NOT_ACCEPTABLE)

        category = Category.objects.get(id=request.data['category'])
        data['category'] = category
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            store = Store.objects.create(**serializer.validated_data, category=category)
            store.save()
            return Response({'id': store.pk, 'name': store.name}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        lon = request.data['lon']
        lat = request.data['lat']

        if lon and lat:
            data['location'] = Point(float(lon), float(lat))

        if 'category' in data:
            category = Category.objects.get(id=request.data['category'])
            data['category'] = category

        store = Store.objects.get(pk=pk)
        serializer = self.serializer_class(store, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response({'id': pk}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    parser_classes = [MultiPartParser]

    def create(self, request):
        store = request.data['store']
        name = request.data['name']
        same_menu = Menu.objects.filter(name=name, store=store)
        if same_menu:
            return Response({'message': 'the same menu exists'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        if request.FILES:
            request.data.image = request.FILES
        serializer = MenuSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        menu = Menu.objects.get(pk=pk)
        if request.FILES:
            data.image = request.FILES
        serializer = self.serializer_class(menu, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def delete_image(self, request, pk=None):
        menu = self.get_object()
        menu.image.delete(save=True)
        menu.save()
        return Response(data={'id': pk}, status=status.HTTP_200_OK)