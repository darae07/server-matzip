from django.db import models
from django.db.models.manager import BaseManager

from matzip.utils.datetime_func import today_min, today_max


class PartyQuerySet(models.QuerySet):
    def get_today_party_list(self):
        return self.filter(created_at__range=(today_min, today_max))


class PartyManager(BaseManager.from_queryset(PartyQuerySet)):
    pass

