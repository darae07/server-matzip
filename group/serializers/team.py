from rest_framework import serializers

from group.models_team import Team
from group.serializers.party import PartyListSerializer
from group.serializers.team_member import TeamMemberSerializer


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        exclude = ('join_code',)


class TeamFindSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = '__all__'


class TeamListSerializer(serializers.ModelSerializer):
    my_membership = serializers.SerializerMethodField('get_my_membership')

    def get_my_membership(self, instance):
        serializer = TeamMemberSerializer(instance=instance.members.first(), many=False, read_only=True)
        return serializer.data

    class Meta:
        model = Team
        exclude = ('join_code',)


class TeamDetailSerializer(serializers.ModelSerializer):
    party = PartyListSerializer(read_only=True, many=True)

    class Meta:
        model = Team
        fields = '__all__'


