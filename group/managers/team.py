from django.db import models
from django.db.models import Q
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext_lazy as _


class TeamMemberQuerySet(models.QuerySet):
    pass


class TeamMemberManager(BaseManager.from_queryset(TeamMemberQuerySet)):
    def get_my_team_profile(self, user):
        if not user:
            raise ValueError(_('유저를 입력해주세요.'))
        return self.filter(user=user.id).order_by('-is_selected').first()

    def select_team(self, user, team):
        if not user:
            raise ValueError(_('유저를 입력해주세요.'))
        my_memberships = self.filter(user=user.id)
        current_team = my_memberships.filter(team=team)
        current_team.update(is_selected=True)
        other_teams = my_memberships.filter(~Q(team=team))
        if current_team.first():
            other_teams.update(is_selected=False)
        return current_team.first()
