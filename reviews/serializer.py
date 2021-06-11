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


class ReplyField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        id = super(ReplyField, self).to_representation(value)
        try:
            replies = Comment.objects.filter(parent_post=id)
            serializer = CommentSerializer(replies)
            return serializer.data
        except Comment.DoseNotExist:
            return None

    def get_replies(self, cutoff=None):
        queryset = self.get_queryset()
        if queryset is None:
            return {}

        return OrderedDict([(item.id, self.display_value(item)) for item in queryset])


class ReviewSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True)
    reply = ReplyField(queryset=Comment.objects.all())

    class Meta:
        model = Review
        fields = ['store_id', 'title', 'content', 'image', 'created_at', 'modified_at']
        extra_kwargs = {'token': {'write_only': True}}
