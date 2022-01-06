from rest_framework import serializers
from common.serializers import UserSerializer
from group.models import TeamMember


class TeamMemberSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = TeamMember
        read_only_fields = ['user']
        fields = '__all__'


class TeamMemberCreateSerializer(serializers.ModelSerializer):
    # user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)

    class Meta:
        model = TeamMember
        fields = '__all__'


