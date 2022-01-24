from django.db.models import Q
from rest_framework import serializers

from common.costume_serializers import FullUserSerializer
from group.constants import MembershipStatus
from group.models_crew import CrewMembership, Crew, Lunch, Vote
from group.serializers.team_member import TeamMemberSerializer
from stores.serializers.keword import KeywordSerializer


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'


class VoteListSerializer(VoteSerializer):
    team_member = TeamMemberSerializer(read_only=True, many=False)


class LunchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lunch
        fields = '__all__'


class LunchListSerializer(LunchSerializer):
    keyword = KeywordSerializer(read_only=True, many=True)
    votes = VoteSerializer(read_only=True, many=True)


class CrewMembershipSerializer(serializers.ModelSerializer):
    user = FullUserSerializer(read_only=True, many=False)
    team_member = TeamMemberSerializer(read_only=True, many=False)
    invite_member = TeamMemberSerializer(read_only=True, many=False)

    class Meta:
        model = CrewMembership
        fields = '__all__'


class CrewMembershipCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrewMembership
        fields = '__all__'


class CrewListSerializer(serializers.ModelSerializer):
    membership = serializers.SerializerMethodField('get_membership')

    def get_membership(self, instance):
        queryset = instance.crew_membership.filter(~Q(status=MembershipStatus.DENIED.value))\
            .order_by('status', '-created_at')
        serializer = CrewMembershipSerializer(queryset, many=True, read_only=True)
        return serializer.data

    class Meta:
        model = Crew
        fields = '__all__'


class CrewDetailSerializer(CrewListSerializer):
    lunches = serializers.SerializerMethodField('get_lunches')

    def get_lunches(self, instance):
        queryset = instance.lunches.get_today_lunch_list()
        serializer = LunchListSerializer(queryset, read_only=True, many=True)
        return serializer.data


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = '__all__'






