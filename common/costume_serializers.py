from group.models_team import Contract
from group.serializer_contract import ContractSerializer
from .serializers import UserSerializer
from rest_framework import serializers


class FullUserSerializer(UserSerializer):
    # contract = serializers.SerializerMethodField('get_contract')
    # contract = ContractSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = ['id', 'email', 'last_login',
                  'date_joined', 'nickname', 'image', 'status', 'phone_number']

    # def get_contract(self, instance):
    #     company = None
    #     request = self.context.get('request')
    #     # print(self.context["request"].query_params.get("company", None))
    #     # print(instance)
    #     if request and hasattr(request, 'data'):
    #         company = request.data.company
    #         print(request.data)
    #     if company:
    #         contract = Contract.objects.filter(company=company)
    #         serializer = ContractSerializer(contract=contract, many=True)
    #         return serializer.data