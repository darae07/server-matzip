from django.db import models
from common.models import CommonUser
from stores.models import Store


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=100)
    employees = models.ManyToManyField(CommonUser, through='Contract')

    def __str__(self):
        return self.name


class Contract(models.Model):
    employee = models.ForeignKey(CommonUser, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    date_joined = models.DateField()
    team_name = models.CharField(max_length=100)

    def __str__(self):
        return self.employee.username


class Party(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(CommonUser, through='Membership')
    description = models.CharField(max_length=500, null=True, blank=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Membership(models.Model):
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE)
    party = models.ForeignKey(Party, on_delete=models.CASCADE)
    date_joined = models.DateField()
    invite_reason = models.CharField(max_length=100, null=True, blank=True)