from rest_framework import serializers

from common.costume_serializers import FullUserSerializer
from group.models_team import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamMember
        read_only_fields = ['user']
        fields = '__all__'


class TeamMemberDetailSerializer(serializers.ModelSerializer):
    user = FullUserSerializer(read_only=True, many=False)

    class Meta:
        model = TeamMember
        fields = '__all__'


class TeamMemberCompactSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeamMember
        fields = ['id', 'image', 'member_name']


class PartyTeamMemberSerializer(serializers.ModelSerializer):
    is_invited_waiting = serializers.BooleanField(read_only=True)
    is_party_member = serializers.BooleanField(read_only=True)

    class Meta:
        model = TeamMember
        read_only_fields = ['user']
        fields = '__all__'


class TeamMemberCreateSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = TeamMember
        fields = '__all__'


