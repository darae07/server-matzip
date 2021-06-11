from django.db import models
from stores.models import Store


# Create your models here.


class ReviewImage(models.Model):
    image = models.ImageField(upload_to='reviews/review', default='')


class Review(models.Model):
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    content = models.TextField()
    image = models.ForeignKey(ReviewImage, on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class Comment(models.Model):
    content = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey(Review, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

