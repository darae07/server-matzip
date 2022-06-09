from common.models import CommonUser
from rest_framework import serializers


class FullUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CommonUser
        fields = ['id', 'email', 'last_login',
                  'date_joined', 'nickname', 'image', 'status', 'phone_number']

