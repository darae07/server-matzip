from rest_framework import serializers
from .models_team import Contract


class ContractSerializer(serializers.ModelSerializer):
    # user = UserSerializer(read_only=True, many=False)

    class Meta:
        model = Contract
        fields = '__all__'