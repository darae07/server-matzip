from group.serializer import ContractSerializer
from .serializers import UserSerializer
from rest_framework import serializers


class FullUserSerializer(UserSerializer):
    # contract = ContractSerializer(read_only=True, many=False)
    contract = serializers.CharField(allow_null=True, allow_blank=True)

    class Meta(UserSerializer.Meta):
        fields = ['id', 'username', 'email', 'last_login',
                  'date_joined', 'nickname', 'image_url', 'status', 'phone_number', 'contract']