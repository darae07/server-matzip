from django.db import models
from stores.models import Store, Menu


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=100)
    lat = models.FloatField(null=True, blank=True)
    lon = models.FloatField(null=True, blank=True)
    title = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Contract(models.Model):
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True, related_name='user')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True, related_name='members')
    date_joined = models.DateField(auto_now_add=True, blank=True)
    team_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username


class Party(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('common.CommonUser', through='Membership')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)


class Membership(models.Model):
    user = models.ForeignKey('common.CommonUser', on_delete=models.CASCADE, null=True, blank=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    date_joined = models.DateField(auto_now_add=True, blank=True)
    invite_reason = models.CharField(max_length=100, null=True, blank=True)
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.user.username
