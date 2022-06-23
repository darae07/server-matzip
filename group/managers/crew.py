from django.db import models
from django.db.models import Count
from django.db.models.manager import BaseManager

from matzip.utils.datetime_func import today


class LunchQuerySet(models.QuerySet):
    def get_today_lunch_list(self):
        return self.filter(created_at=today)\
            .annotate(vote_count=Count('votes')).order_by('-vote_count')


class LunchManager(BaseManager.from_queryset(LunchQuerySet)):
    pass
