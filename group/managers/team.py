from django.db import models
from django.db.models.manager import BaseManager
from django.utils.translation import ugettext_lazy as _


class TeamMemberQuerySet(models.QuerySet):
    pass


class TeamMemberManager(BaseManager.from_queryset(TeamMemberQuerySet)):
    def get_my_team_profile(self, user):
        if not user:
            raise ValueError(_('유저를 입력해주세요.'))
        return self.filter(user=user.id).order_by('-is_selected').first()

