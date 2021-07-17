from collections import OrderedDict

from rest_framework import serializers
from .models import Review, ReviewImage, Comment
from common.serializers import UserSerializer


class ReviewImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ReviewImage
        fields = ['image_url']

    def get_image_url(self, queryset):
        request = self.context.get('request')
        image_url = queryset.image.url
        return request.build_absolute_uri(image_url)


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    images = ReviewImageSerializer(read_only=True, many=True)
    comments = CommentSerializer(read_only=True, many=True)
    user = UserSerializer(read_only=True)
    my_name = serializers.CharField(allow_null=True)

    class Meta:
        model = Review
        fields = '__all__'

