from django.db import models
from common.models import CommonUser


# Create your models here.
class Party(models.Model):
    name = models.CharField(max_length=200)
    members = models.ManyToManyField(CommonUser, through='Membership')

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=100, null=True, blank=True)