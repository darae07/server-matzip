from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, AbstractUser


class CommonUser(AbstractUser):
    nickname = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=400, null=True, blank=True)
    image = models.ImageField(upload_to='users', default='', null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         Profile.objects.create(user=instance, user_pk=instance.id)
#
#
# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.profile.save()
