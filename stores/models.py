from django.db import models
from django.db.models import Q
from haversine import haversine
from django.contrib.gis.db.models import PointField
from group.models_team import Team
from stores.managers.keyword import KeywordManager


class Category(models.Model):
    name = models.CharField(max_length=50, default='')

    def __str__(self):
        return self.name


# Create your models here.
class StoreManager(models.Manager):
    def with_distance(self, position):
        condition = (
                Q(lat__range=(position[0] - 0.005, position[0] + 0.005)) |
                Q(lon__range=(position[1] - 0.007, position[1] + 0.007))
        )
        queryset = self.filter(condition)
        near_store_ids = [store.id for store in queryset
                          if haversine(position, (store.lat, store.lon)) <= 2]
        queryset = queryset.filter(id__in=near_store_ids)
        queryset = queryset.annotate(distance=haversine(position, ('lat', 'lon'), unit='m'))
        return queryset


class Store(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    location = PointField(srid=4326, geography=True, blank=True, null=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    objects = models.Manager()
    store_objects = StoreManager()

    def __str__(self):
        return self.name


class Keyword(models.Model):
    name = models.CharField(default=None, max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    hit_count = models.IntegerField(default=0)
    eat_count = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    objects = KeywordManager()

    def __str__(self):
        return self.name


class Menu(models.Model):
    store = models.ForeignKey(Store, related_name='menus', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    image = models.ImageField(upload_to='stores/menu', default='', null=True, blank=True)

    def __str__(self):
        return self.name
