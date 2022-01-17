from django.db.models import Count

from reviews.serializer import ReviewListSerializer
from .constants import InviteStatus
from .models_crew import Vote
from .models_party import Membership, Party
from .models_team import Company, Contract
from rest_framework import serializers
from .models_team import Invite, Tag
from common.costume_serializers import FullUserSerializer
from group.serializers.team_member import TeamMemberSerializer


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Contract
        fields = '__all__'


class CompanyMemberSerializer(serializers.ModelSerializer):
    members = ContractSerializer(read_only=True, many=True)

    class Meta:
        model = Company
        fields = '__all__'


class VoteListSerializer(serializers.ModelSerializer):
    team_member = TeamMemberSerializer(read_only=True, many=False)

    class Meta:
        model = Vote
        fields = '__all__'


class VoteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vote
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    team_member = TeamMemberSerializer(read_only=True, many=False)
    votes = VoteListSerializer(read_only=True, many=True)

    class Meta:
        model = Tag
        fields = '__all__'


class TagDetailSerializer(serializers.ModelSerializer):
    team_member = TeamMemberSerializer(read_only=True, many=False)
    votes = VoteListSerializer(read_only=True, many=True)
    review = serializers.SerializerMethodField('get_review')

    def get_review(self, instance):
        serializer = ReviewListSerializer(instance=instance.review, read_only=True, many=False,
                                          context={'team': self.context['team']})
        return serializer.data

    class Meta:
        model = Tag
        fields = '__all__'


class TagListSerializer(serializers.ModelSerializer):
    team_member = TeamMemberSerializer(read_only=True, many=False)
    review = serializers.SerializerMethodField('get_review')

    def get_review(self, instance):
        serializer = ReviewListSerializer(instance=instance.review, read_only=True, many=False,
                                          context={'team': self.context['team']})
        return serializer.data

    class Meta:
        model = Tag
        fields = '__all__'


class TagCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class InviteSerializer(serializers.ModelSerializer):
    # team = TeamSerializer(read_only=True, many=False)
    sender = TeamMemberSerializer(read_only=True, many=False)

    class Meta:
        model = Invite
        fields = '__all__'


class InviteDetailSerializer(serializers.ModelSerializer):
    # team = TeamSerializer(read_only=True, many=False)
    sender = TeamMemberSerializer(read_only=True, many=False)
    receiver = TeamMemberSerializer(read_only=True, many=False)

    class Meta:
        model = Invite
        fields = '__all__'


class InviteCreateSerializer(serializers.ModelSerializer):
    # party = PartySerializer(read_only=True, many=False)
    party_id = serializers.IntegerField(write_only=True)
    # team = serializers.RelatedField(read_only=True, required=True)
    # sender = serializers.RelatedField(read_only=True, required=True)

    class Meta:
        model = Invite
        fields = '__all__'



