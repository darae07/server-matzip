from django.db import models
from stores.models import Store
from common.models import CommonUser


# Create your models here.
class Review(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    user = models.ForeignKey(CommonUser, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=300)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    star = models.PositiveSmallIntegerField(default=0)
    public = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ReviewImage(models.Model):
    image = models.ImageField(upload_to='reviews/review', default='')
    review = models.ForeignKey(Review, related_name='images', on_delete=models.CASCADE, null=True)


class Comment(models.Model):
    user_id = models.ForeignKey(CommonUser, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent_post = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.content
