from django.db.models import F, Q
from rest_framework import serializers

from common.costume_serializers import FullUserSerializer
from group.constants import MembershipStatus
from group.models_party import Party, Membership
from group.serializers.team_member import TeamMemberSerializer


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

    def get_membership(self, instance):
        queryset = instance.membership.filter(status=~Q(MembershipStatus.DENIED.value))\
            .order_by('status', '-created_at')
        serializer = MembershipSerializer(queryset, many=True)
        return serializer.data

    class Meta:
        model = Party
        fields = '__all__'


class PartyDetailSerializer(serializers.ModelSerializer):
    membership = MembershipSerializer(read_only=True, many=True)

    class Meta:
        model = Party
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = '__all__'
        list_serializer_class = PartyListSerializer

