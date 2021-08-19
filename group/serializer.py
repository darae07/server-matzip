from django.utils.dateparse import parse_datetime
from .models import Company, Contract
from rest_framework import serializers
from common.serializers import UserSerializer
from .models import Vote, Party, Membership, Invite
from stores.serializer import StoreSerializer
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


class MembershipCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Membership
        fields = '__all__'


class PartyListSerializer(serializers.ModelSerializer):
    company = CompanySerializer(read_only=True, many=False)
    membership = MembershipSerializer(read_only=True, many=True)
    votes = VoteSerializer(read_only=True, many=False)

    class Meta:
        model = Party
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):
    members = MembershipSerializer(read_only=True, many=True)

    class Meta:
        model = Party
        fields = '__all__'
        list_serializer_class = PartyListSerializer

    def create(self, validated_data):
        s = self.data['date']
        date = parse_datetime(s)
        data = validated_data
        data['date'] = date
        return Party.objects.create(**data)

    def update(self, instance, validated_data):
        instance.company = validated_data.get('company', instance.company)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.date = parse_datetime(self.data['date'])
        instance.save()
        return instance


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
