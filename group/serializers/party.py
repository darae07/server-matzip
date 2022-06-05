from django.db.models import F, Q
from rest_framework import serializers

from common.costume_serializers import FullUserSerializer
from group.constants import MembershipStatus
from group.models_party import Party, Membership
from group.serializers.team_member import TeamMemberSerializer
from reviews.models import Review
from reviews.serializers.review import ReviewListSerializer
from stores.serializers.keword import KeywordSerializer


class MembershipSerializer(serializers.ModelSerializer):
    user = FullUserSerializer(read_only=True, many=False)
    team_member = TeamMemberSerializer(read_only=True, many=False)
    invite_member = TeamMemberSerializer(read_only=True, many=False)
    # vote = VoteSerializer(read_only=True, many=False)

    class Meta:
        model = Membership
        fields = '__all__'


class MembershipCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = '__all__'


class PartyListSerializer(serializers.ModelSerializer):
    membership = serializers.SerializerMethodField('get_membership')
    keyword = KeywordSerializer(read_only=True, many=False)

    def get_membership(self, instance):
        queryset = instance.membership.filter(~Q(status=MembershipStatus.DENIED.value))\
            .order_by('status', '-created_at')
        serializer = MembershipSerializer(queryset, many=True, read_only=True)
        return serializer.data

    class Meta:
        model = Party
        fields = '__all__'


class PartyDetailSerializer(PartyListSerializer):
    reviews = serializers.SerializerMethodField('get_reviews')

    def get_reviews(self, instance):
        queryset = Review.objects.filter(keyword=instance.keyword).order_by('-created_at')[:5]
        serializer = ReviewListSerializer(queryset, read_only=True, many=True)
        return serializer.data

    class Meta:
        model = Party
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = '__all__'
        list_serializer_class = PartyListSerializer


