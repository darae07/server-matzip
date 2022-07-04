from django.db import models
from django.db.models.manager import BaseManager


class KeywordQuerySet(models.QuerySet):
    def get_keyword(self, name, team):
        return self.filter(name=name, team=team).first()


class KeywordManager(BaseManager.from_queryset(KeywordQuerySet)):
    def hit_keyword(self, name, use_kakaomap, use_team_location, team, category):
        keyword = self.get_queryset().get_keyword(name, team)
        if keyword:
            keyword.hit_count += 1
        else:
            keyword = self.model(name=name, team=team, category=category, hit_count=1,
                                 use_kakaomap=use_kakaomap, use_team_location=use_team_location )
        keyword.save()
        return keyword

