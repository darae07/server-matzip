from django.contrib.auth.models import User, AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .managers import CustomUserManager


class CommonUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    nickname = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=400, null=True, blank=True)
    image = models.ImageField(upload_to='users', default='', null=True, blank=True)
    status = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
