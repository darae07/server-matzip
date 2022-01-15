from django.db import models
from .constants import MembershipStatus
from stores.models import Keyword


class Party(models.Model):
    name = models.CharField(max_length=100)
    team = models.ForeignKey('group.Team', on_delete=models.CASCADE, null=True, blank=True, related_name='party')
    description = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    eat = models.BooleanField(default=False)
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True)
    team_member = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='membership')
    date_joined = models.DateTimeField(auto_now_add=True, blank=True)
    invite_reason = models.CharField(max_length=100, null=True, blank=True)
    status = models.SmallIntegerField(default=MembershipStatus.ALLOWED.value)

    def __str__(self):
        return self.team_member.member_name