from group.serializer import ContractSerializer
from .serializers import UserSerializer


class FullUserSerializer(UserSerializer):
    contract = ContractSerializer(read_only=True, many=True)

    class Meta(UserSerializer.Meta):
        fields = ['id', 'username', 'email', 'last_login',
                  'date_joined', 'nickname', 'image_url', 'status', 'phone_number', 'contract']