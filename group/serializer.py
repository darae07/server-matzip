from .models import Company
from rest_framework import serializers
from common.models import CommonUser


class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ['name']


