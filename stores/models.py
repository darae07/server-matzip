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


class Keyword(models.Model):
    name = models.CharField(default=None, max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    hit_count = models.IntegerField(default=0)
    eat_count = models.IntegerField(default=0)
    good_count = models.IntegerField(default=0)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    use_kakaomap = models.BooleanField(default=True)
    use_team_location = models.BooleanField(default=True)

    objects = KeywordManager()

    def __str__(self):
        return self.name
