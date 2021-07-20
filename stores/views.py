from django.db.models import OuterRef, Avg, Subquery
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

# Create your views here.


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    pagination.PageNumberPagination.page_size = 20

    filter_backends = [SearchFilter]
    search_fields = 'name'
    company = None

    def list(self, request, *args, **kwargs):
        queryset = Store.objects.all()
        name = request.query_params.get('name')
        category = request.query_params.get('category')
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')
        near = request.query_params.get('near')
        order = request.query_params.get('order')
        user = request.user

        # is user joined company?
        contract = Contract.objects.filter(user_id=user).first()
        if contract:
            company_id = contract.company_id
            self.company = Company.objects.get(pk=company_id)

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
        store_reviews = Review.objects.filter(store=OuterRef('pk')).order_by().values('store')
        avg_stars = store_reviews.annotate(avg_star=Avg('star')).values('avg_star')
        queryset = queryset.annotate(review_stars=Subquery(avg_stars))

        if self.company:
            company_members = Contract.objects.filter(company=self.company.id).values('user')
            members_store_reviews = store_reviews.filter(user__in=company_members)
            member_avg_stars = members_store_reviews.annotate(member_avg_star=Avg('star')).values('member_avg_star')
            queryset = queryset.annotate(members_stars=Subquery(member_avg_stars))

        if order is not None:
            if order == 'review':
                queryset = queryset.order_by('review_stars')
            if order == 'distance' and near is not None:
                queryset = queryset.order_by('distance')

        serializer = self.serializer_class(queryset, many=True)
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
                                status=status.HTTP_400_BAD_REQUEST)

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
