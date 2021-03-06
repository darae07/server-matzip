import uuid
from django.db import models
from django.contrib.gis.db.models import PointField
import os
from .constants import InviteStatus
from .managers.team import TeamMemberManager


def unique_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('group/team', filename)


def unique_path2(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('group/member', filename)


def _create_id():
    return uuid.uuid4().hex[:6].upper()


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=unique_path, default='')
    title = models.CharField(max_length=300, blank=True, null=True)
    join_code = models.CharField(max_length=8, editable=False, default=_create_id, unique=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    location = models.CharField(default=None, max_length=20)

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    team = models.ForeignKey('group.Team', on_delete=models.CASCADE, null=True, blank=True, related_name='members')
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='team_membership')
    member_name = models.CharField(max_length=100, default='')
    date_joined = models.DateTimeField(auto_now_add=True, blank=True)
    image = models.ImageField(upload_to=unique_path2, default='')
    title = models.CharField(max_length=6, blank=True, null=True)
    is_selected = models.BooleanField(default=True)

    objects = TeamMemberManager()
    
    def __str__(self):
        return self.member_name


class Invite(models.Model):
    party = models.ForeignKey('group.Party', on_delete=models.CASCADE, null=True, blank=True, related_name='party')
    sender = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='sender')
    receiver = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='receiver')
    date_invited = models.DateTimeField(auto_now_add=True, blank=True)
    status = models.SmallIntegerField(default=InviteStatus.WAITING.value)

    def __str__(self):
        return self.receiver.member_name


class Company(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = PointField(srid=4326, geography=True, blank=True, null=True)
    title = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Contract(models.Model):
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='contract')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='members')
    date_joined = models.DateTimeField(auto_now_add=True, blank=True)
    team_name = models.CharField(max_length=100, null=True, blank=True)
    my_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.email


class Tag(models.Model):
    party = models.ForeignKey('group.Party', on_delete=models.CASCADE, null=True, blank=True, related_name='tags')
    team_member = models.ForeignKey('group.TeamMember', on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey('reviews.Review', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

