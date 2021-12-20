from rest_framework import serializers
from .models import Review, ReviewImage, Comment
from common.costume_serializers import FullUserSerializer
from group.serializer import TeamMemberSerializer
from group.models import TeamMember


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
                try:
                    team_member = TeamMember.objects.get(team=team, user=instance.user)
                except TeamMember.DoesNotExist:
                    team_member = None
                if team_member:
                    serializer = TeamMemberSerializer(instance=team_member, read_only=True)
                    return serializer.data
        return None

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
    team_member = TeamMemberSerializer(read_only=True, many=False)
    requires_context = True

    class Meta(ReviewSerializer.Meta):
        fields = '__all__'

    def get_comments(self, instance):
        print(self.context['request'].query_params.get('team'))
        comments = Comment.objects.filter(parent_comment=None, parent_post=instance).order_by('-created_at')
        serializer = CommentListSerializer(instance=comments, many=True, context={'request': self.context['request']})
        return serializer.data
