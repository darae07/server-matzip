from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import CommonUser
# Register your models here.



# class UserAdmin(BaseUserAdmin):
#     inlines = (ProfileInline,)


# admin.site.unregister(CommonUser)
admin.site.register(CommonUser, UserAdmin)