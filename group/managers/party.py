from django.db import models
from django.db.models.manager import BaseManager
from matzip.utils.datetime_func import today


class PartyQuerySet(models.QuerySet):
    def get_today_party_list(self):
        return self.filter(created_at=today)


class PartyManager(BaseManager.from_queryset(PartyQuerySet)):
    pass

