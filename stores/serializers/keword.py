from rest_framework import serializers
from django.db.models import Avg
from stores.models import Keyword
from stores.serializer import CategorySerializer


class KeywordCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Keyword
        fields = '__all__'


class KeywordSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True, many=False)
    score = serializers.SerializerMethodField('get_score')

    def get_score(self, instance):
        return instance.reviews.all().aggregate(Avg('score'))['score__avg']

    class Meta:
        model = Keyword
        fields = '__all__'
