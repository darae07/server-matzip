from django.db import models
from stores.models import Store
from common.models import CommonUser
from stores.models import Category
import uuid
import os
from django.contrib.gis.db.models import PointField
from cloudinary.models import CloudinaryField
from PIL import Image
from .constants import LikeStatus


# Create your models here.
class Review(models.Model):
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE, null=True, blank=True)
    store_name = models.CharField(max_length=100, default='')
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    star = models.PositiveSmallIntegerField(default=0)
    public = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    menu = models.CharField(max_length=100, null=True, blank=True)
    price = models.IntegerField(default=0)
    location = PointField(srid=4326, geography=True, blank=True, null=True)
    address = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.store_name


def unique_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('reviews/review', filename)


class ReviewImage(models.Model):
    image = models.ImageField(upload_to=unique_path, default='')
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE, null=True)


class Comment(models.Model):
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True,
                                       related_name='child_comments')

    def __str__(self):
        return self.content


class Like(models.Model):
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE, null=True, blank=True)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    status = models.SmallIntegerField(default=LikeStatus.ACTIVE.value)
    created_at = models.DateTimeField(auto_now_add=True)
