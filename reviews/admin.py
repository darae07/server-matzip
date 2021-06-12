from django.contrib import admin
from .models import Review, ReviewImage, Comment
# Register your models here.

admin.site.register(ReviewImage)
admin.site.register(Review)
admin.site.register(Comment)
