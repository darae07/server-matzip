from collections import OrderedDict

from rest_framework import serializers
from .models import Review, ReviewImage, Comment
from common.costume_serializers import FullUserSerializer


class ReviewImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ReviewImage
        fields = ['image', 'review']


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'


class CommentListSerializer(CommentSerializer):
    user = FullUserSerializer(read_only=True)
    child_comments = serializers.SerializerMethodField()

    class Meta(CommentSerializer.Meta):
        fields = '__all__'

    def get_child_comments(self, instance):
        serializer = self.__class__(instance.child_comments, many=True)
        serializer.bind('', self)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ReviewListSerializer(ReviewSerializer):
    images = ReviewImageSerializer(read_only=True, many=True)
    comments = serializers.SerializerMethodField('get_comments')
    user = FullUserSerializer(read_only=True)

    class Meta(ReviewSerializer.Meta):
        fields = '__all__'

    def get_comments(self, instance):
        comments = Comment.objects.filter(parent_comment=None, parent_post=instance).order_by('-created_at')
        serializer = CommentListSerializer(instance=comments, many=True)
        return serializer.data


