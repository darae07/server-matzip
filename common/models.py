import os
import uuid

from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager


def unique_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('user', filename)


class CommonUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    nickname = models.CharField(max_length=100, null=True, blank=True, unique=True)
    title = models.CharField(max_length=400, null=True, blank=True)
    image = models.ImageField(upload_to=unique_path, default='')
    status = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    LOGIN_EMAIL = 'email'
    LOGIN_KAKAO = 'kakao'
    LOGIN_GOOGLE = 'google'
    LOGIN_CHOICES = (
        (LOGIN_EMAIL, 'email'),
        (LOGIN_GOOGLE, 'google'),
        (LOGIN_KAKAO, 'kakao')
    )

    login_method = models.CharField(
        max_length=6, choices=LOGIN_CHOICES, default=LOGIN_EMAIL
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
