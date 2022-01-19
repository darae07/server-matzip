from rest_framework import serializers

from stores.models import Keyword
from stores.serializer import CategorySerializer


class KeywordCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Keyword
        fields = '__all__'


class KeywordSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True, many=False)

    class Meta:
        model = Keyword
        fields = '__all__'
