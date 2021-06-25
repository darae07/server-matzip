from .models import Company, Contract
from rest_framework import serializers
from common.models import CommonUser
from common.serializers import UserSerializer


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['name']


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
