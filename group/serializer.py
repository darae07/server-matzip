from .models import Company, Contract
from rest_framework import serializers
from common.models import CommonUser
from common.serializers import UserSerializer
from .models import Vote, Party, Membership, Invite
from stores.serializer import StoreSerializer, MenuSerializer
from common.costume_serializers import FullUserSerializer


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


class VoteSerializer(serializers.ModelSerializer):
    store = StoreSerializer(read_only=True, many=False)

    class Meta:
        model = Vote
        fields = '__all__'


class MembershipSerializer(serializers.ModelSerializer):
    user = FullUserSerializer(read_only=True, many=False)
    vote = VoteSerializer(read_only=True, many=False)

    class Meta:
        model = Membership
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True, many=False)
    membership = MembershipSerializer(read_only=True, many=True)
    votes = VoteSerializer(read_only=True, many=False)

    class Meta:
        model = Party
        fields = '__all__'


class InviteSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True, many=False)
    sender = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Invite
        fields = '__all__'


class InviteCreateSerializer(serializers.ModelSerializer):
    # company = serializers.RelatedField(read_only=True, required=True)
    # sender = serializers.RelatedField(read_only=True, required=True)

    class Meta:
        model = Invite
        fields = '__all__'
