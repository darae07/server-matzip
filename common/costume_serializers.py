from group.serializer_contract import ContractSerializer
from .serializers import UserSerializer


class FullUserSerializer(UserSerializer):
    contract = ContractSerializer(read_only=True, many=True)

    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'last_login',
                  'date_joined', 'nickname', 'image', 'status', 'phone_number', 'contract']