from django.db import models
from django.db.models.manager import BaseManager
from matzip.utils.datetime_func import today_min, today_max, today


class PartyQuerySet(models.QuerySet):
    def get_today_party_list(self):
        return self.filter(created_at__lte=today_max, created_at__gte=today_min)


class PartyManager(BaseManager.from_queryset(PartyQuerySet)):
    pass

