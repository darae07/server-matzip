from django.db.models import Count
from django.utils.dateparse import parse_datetime

from reviews.serializer import ReviewListSerializer
from .constants import InviteStatus
from .models_crew import Vote
from .models_party import Membership, Party
from .models_team import Company, Contract, Team, TeamMember
from rest_framework import serializers
from .models_team import Invite, Tag
from stores.serializer import StoreSerializer
from common.costume_serializers import FullUserSerializer
from .serializer_team_member import TeamMemberSerializer


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


class MembershipSerializer(serializers.ModelSerializer):
    user = FullUserSerializer(read_only=True, many=False)
    team_member = TeamMemberSerializer(read_only=True, many=False)
    # vote = VoteSerializer(read_only=True, many=False)

    class Meta:
        model = Membership
        fields = '__all__'


class MembershipCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
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


class PartyListSerializer(serializers.ModelSerializer):
    membership = MembershipSerializer(read_only=True, many=True)
    tag = serializers.SerializerMethodField('get_tag')

    def get_tag(self, instance):
        if not instance.tags.count():
            return None
        tag = instance.tags.annotate(count=Count('votes')).order_by('-count').first()
        serializer = TagListSerializer(instance=tag, read_only=True, many=False,
                                       context={'team': instance.team.id})
        return serializer.data

    class Meta:
        model = Party
        fields = '__all__'


class PartyDetailSerializer(serializers.ModelSerializer):
    membership = MembershipSerializer(read_only=True, many=True)
    tags = serializers.SerializerMethodField('get_tags')
    invites = serializers.SerializerMethodField('get_invites')

    def get_tags(self, instance):
        serializer = TagDetailSerializer(instance=instance.tags, read_only=True, many=True,
                                         context={'team': instance.team.id})
        return serializer.data

    def get_invites(self, instance):
        invites = Invite.objects.filter(party=instance.id, status=InviteStatus.WAITING.value)
        serializer = InviteDetailSerializer(instance=invites, read_only=True, many=True)
        return serializer.data

    class Meta:
        model = Party
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = '__all__'
        list_serializer_class = PartyListSerializer


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


class InviteSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True, many=False)
    sender = TeamMemberSerializer(read_only=True, many=False)

    class Meta:
        model = Invite
        fields = '__all__'


class InviteDetailSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True, many=False)
    sender = TeamMemberSerializer(read_only=True, many=False)
    receiver = TeamMemberSerializer(read_only=True, many=False)

    class Meta:
        model = Invite
        fields = '__all__'


class InviteCreateSerializer(serializers.ModelSerializer):
    party = PartySerializer(read_only=True, many=False)
    party_id = serializers.IntegerField(write_only=True)
    # team = serializers.RelatedField(read_only=True, required=True)
    # sender = serializers.RelatedField(read_only=True, required=True)

    class Meta:
        model = Invite
        fields = '__all__'



