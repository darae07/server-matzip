from django.db import models
from stores.models import Store, Menu
from django.contrib.gis.db.models import PointField


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=100)
    location = PointField(srid=4326, geography=True, blank=True, null=True)
    title = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Contract(models.Model):
    user = models.OneToOneField('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                                related_name='contract', unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True,
                                related_name='members')
    date_joined = models.DateField(auto_now_add=True, blank=True)
    team_name = models.CharField(max_length=100, null=True, blank=True)
    my_name = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Party(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('common.CommonUser', through='Membership')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='company')
    description = models.CharField(max_length=500, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True, related_name='store')
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True, related_name='menu')
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return self.store.name


class Membership(models.Model):
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, related_name='membership')
    date_joined = models.DateField(auto_now_add=True, blank=True)
    invite_reason = models.CharField(max_length=100, null=True, blank=True)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, null=True, blank=True)
    status = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.user.username


class Invite(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, )
    sender = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                               related_name='sender')
    receiver = models.OneToOneField('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True,
                                    related_name='receiver', unique=True)
    date_invited = models.DateField(auto_now_add=True, blank=True)

    def __str__(self):
        return self.receiver.username
