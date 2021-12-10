import os
import uuid

from django.db import models
from stores.models import Store, Menu
from django.contrib.gis.db.models import PointField


def unique_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('group/team', filename)


class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=unique_path, default='')
    title = models.CharField(max_length=300, blank=True, null=True)


class TeamMember(models.Model):
    team = models.ForeignKey('group.Team', on_delete=models.CASCADE, null=True, blank=True, related_name='members')
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                             related_name='team_membership')
    member_name = models.CharField(max_length=100, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True, blank=True)


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
    date_joined = models.DateField(auto_now_add=True, blank=True)
    team_name = models.CharField(max_length=100, null=True, blank=True)
    my_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.email


class Party(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('common.CommonUser', through='Membership')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='company')
    description = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='membership')
    date_joined = models.DateField(auto_now_add=True, blank=True)
    invite_reason = models.CharField(max_length=100, null=True, blank=True)
    status = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.user.email


class Vote(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, related_name='store')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True, related_name='menu')
    membership = models.OneToOneField(Membership, null=True, blank=True, related_name='vote', on_delete=models.CASCADE)

    def __str__(self):
        return self.store.name


class Invite(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, )
    sender = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='sender')
    receiver = models.OneToOneField('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='receiver')
    date_invited = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.receiver.email
