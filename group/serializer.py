from .models import Company, Contract
from rest_framework import serializers
from common.models import CommonUser
from common.serializers import UserSerializer
from .models import Vote, Party, Membership
from stores.serializer import StoreSerializer, MenuSerializer


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'


class ContractSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True, many=False)

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
    user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Membership
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):
    votes = VoteSerializer(read_only=True, many=True)
    company = CompanySerializer(read_only=True, many=False)
    members = UserSerializer(read_only=True, many=True)

    class Meta:
        model = Party
        fields = '__all__'
