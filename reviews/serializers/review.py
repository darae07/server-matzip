from rest_framework import serializers

from group.serializers.team_member import TeamMemberSerializer
from reviews.models import Review, ReviewImage
from stores.serializers.keword import KeywordSerializer


class ReviewImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReviewImage
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'


class ReviewListSerializer(ReviewSerializer):
    team_member = TeamMemberSerializer(read_only=True, many=False)
    images = serializers.SerializerMethodField('get_images')

    def get_images(self, instance):
        queryset = instance.images.all()
        if not queryset.count():
            return None
        serializer = ReviewImageSerializer(queryset, many=True)
        return serializer.data


class MyReviewListSerializer(ReviewListSerializer):
    keyword = KeywordSerializer(read_only=True, many=False)


class ReviewMemberListSerializer(ReviewSerializer):
    team_member = TeamMemberSerializer(read_only=True, many=False)
