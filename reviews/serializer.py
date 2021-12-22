from rest_framework import serializers
from .models import Review, ReviewImage, Comment, Like
from common.costume_serializers import FullUserSerializer
from group.serializer import TeamMemberSerializer, TeamMemberCreateSerializer
from group.models import TeamMember
from .constants import LikeStatus


def get_team_member(team, instance):
    if team:
        try:
            team_member = TeamMember.objects.get(team=team, user=instance.user)
        except TeamMember.DoesNotExist:
            team_member = None
        if team_member:
            serializer = TeamMemberCreateSerializer(instance=team_member, read_only=True)
            return serializer.data
    return None


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
    team_member = serializers.SerializerMethodField('get_team_member')

    class Meta(CommentSerializer.Meta):
        fields = '__all__'

    def get_team_member(self, instance):
        if self.context['request']:
            team = self.context['request'].query_params.get('team')
            if team:
                return get_team_member(team, instance)
        return None

    def get_child_comments(self, instance):
        serializer = self.__class__(instance.child_comments, many=True)
        serializer.bind('', self)
        return serializer.data


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'


class LikeInReviewListSerializer(LikeSerializer):
    user = FullUserSerializer(read_only=True)
    team_member = serializers.SerializerMethodField('get_team_member')

    class Meta(LikeSerializer.Meta):
        fields = '__all__'

    def get_team_member(self, instance):
        if self.context['request']:
            team = self.context['request'].query_params.get('team')
            if team:
                return get_team_member(team, instance)
        return None


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ReviewListSerializer(ReviewSerializer):
    images = ReviewImageSerializer(read_only=True, many=True)
    user = FullUserSerializer(read_only=True)
    team_member = serializers.SerializerMethodField('get_team_member')
    requires_context = True
    likes = serializers.SerializerMethodField('get_likes')

    class Meta(ReviewSerializer.Meta):
        fields = '__all__'

    def get_team_member(self, instance):
        if self.context['request']:
            team = self.context['request'].query_params.get('team')
            if team:
                return get_team_member(team, instance)
        return None

    def get_likes(self, instance):
        likes = Like.objects.filter(status=LikeStatus.ACTIVE.value, review=instance).order_by('-created_at')
        serializer = LikeSerializer(instance=likes, many=True)
        return serializer.data


class ReviewRetrieveSerializer(ReviewListSerializer):
    comments = serializers.SerializerMethodField('get_comments')

    class Meta(ReviewListSerializer.Meta):
        fields = '__all__'

    def get_comments(self, instance):
        comments = Comment.objects.filter(parent_comment=None, parent_post=instance).order_by('-created_at')
        serializer = CommentListSerializer(instance=comments, many=True, context={'request': self.context['request']})
        return serializer.data

    def get_likes(self, instance):
        likes = Like.objects.filter(status=LikeStatus.ACTIVE.value, review=instance).order_by('-created_at')
        serializer = LikeInReviewListSerializer(instance=likes, many=True, context={'request': self.context['request']})
        return serializer.data


class LikeListSerializer(LikeInReviewListSerializer):
    review = ReviewListSerializer(read_only=True, many=False)

    class Meta(LikeInReviewListSerializer.Meta):
        fields = '__all__'

