from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.renderers import JSONRenderer
import json
from django.core.serializers import serialize
from .models import CommonUser
from group.serializer import ContractSerializer


class LoginSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    def get_image_url(self, queryset):
        request = self.context.get('request')
        if not queryset.image:
            return None
        image_url = queryset.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = CommonUser
        fields = ['id', 'username', 'email', 'last_login', 'is_superuser', 'is_staff',
                  'date_joined', 'nickname', 'image_url', 'status', 'phone_number']


class UserSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    contract = ContractSerializer(read_only=True, many=False)

    def get_image_url(self, queryset):
        request = self.context.get('request')
        if not queryset.image:
            return None
        image_url = queryset.image.url
        return request.build_absolute_uri(image_url)

    class Meta:
        model = CommonUser
        fields = ['id', 'username', 'email', 'last_login',
                  'date_joined', 'nickname', 'image_url', 'status', 'phone_number', 'contract']


