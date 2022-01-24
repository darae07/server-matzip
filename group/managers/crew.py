from django.db import models
from django.db.models.manager import BaseManager

from matzip.utils.datetime_func import today_min, today_max


class LunchQuerySet(models.QuerySet):
    def get_today_lunch_list(self):
        return self.filter(created_at__range=(today_min, today_max))


class LunchManager(BaseManager.from_queryset(LunchQuerySet)):
    pass