from django.db import models
from stores.models import Store


# Create your models here.
class Review(models.Model):
    store_id = models.ForeignKey(Store, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)


class ReviewImage(models.Model):
    image = models.ImageField(upload_to='reviews/review', default='')
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE, null=True)


class Comment(models.Model):
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

