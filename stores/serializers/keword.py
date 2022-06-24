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
    eat_count = serializers.SerializerMethodField('get_eat_count')
    good_count = serializers.SerializerMethodField('get_good_count')

    def get_score(self, instance):
        return instance.reviews.all().aggregate(Avg('score'))['score__avg']

    def get_eat_count(self, instance):
        return instance.reviews.all().count()

    def get_good_count(self, instance):
        reviews = instance.reviews.all()
        return reviews.filter(score__gte=4).count()

    class Meta:
        model = Keyword
        fields = '__all__'
