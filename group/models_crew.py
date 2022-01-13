from django.db import models
from stores.models import Keyword


class Vote(models.Model):
    team_member = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True)
    party = models.ForeignKey('group.Party', on_delete=models.CASCADE, null=True, blank=True)
    tag = models.ForeignKey('group.Tag', on_delete=models.CASCADE, null=True, blank=True, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.team_member.member_name


class Lunch(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    title = models.CharField(default=None, max_length=300)
    date = models.DateField(auto_now_add=True)
    eat = models.BooleanField(default=False)
