import os
import uuid
from django.db import models
from group.constants import MembershipStatus
from group.managers.crew import LunchManager
from stores.models import Keyword


class Vote(models.Model):
    team_member = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True)
    lunch = models.ForeignKey('group.Lunch', on_delete=models.CASCADE, null=True, blank=True, related_name='votes')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.team_member.member_name


class Lunch(models.Model):
    keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)
    title = models.CharField(default=None, max_length=300)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    eat = models.BooleanField(default=False)
    crew = models.ForeignKey('group.Crew', on_delete=models.CASCADE, null=True, blank=True, related_name='lunches')

    objects = LunchManager()

    def __str__(self):
        return self.title


def unique_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('group/crew', filename)


class Crew(models.Model):
    name = models.CharField(default=None, max_length=100)
    image = models.ImageField(upload_to=unique_path, default='')
    title = models.CharField(default=None, max_length=300, null=True, blank=True)
    team = models.ForeignKey('group.Team', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class CrewMembership(models.Model):
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True)
    team_member = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='crew_team_profile')
    crew = models.ForeignKey(Crew, on_delete=models.CASCADE, related_name='crew_membership')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_joined = models.DateTimeField(blank=True, null=True)
    invite_reason = models.CharField(max_length=100, null=True, blank=True)
    invite_member = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='crew_sender_profile')
    status = models.SmallIntegerField(default=MembershipStatus.ALLOWED.value)

    def __str__(self):
        return self.team_member.member_name