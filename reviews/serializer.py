from collections import OrderedDict

from rest_framework import serializers
from .models import Review, ReviewImage, Comment


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ['image']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['store_id', 'title', 'content', 'created_at', 'modified_at']


class ReviewSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True)
    comments = serializers.StringRelatedField(many=True)

    class Meta:
        model = Review
        fields = ['store_id', 'title', 'content', 'created_at', 'images', 'comments']
        extra_kwargs = {'token': {'write_only': True}}
