from rest_framework import serializers
from .models import Store, Category, Menu


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = Menu
        fields = ['store', 'name', 'price', 'id', 'image']


class StoreSerializer(serializers.ModelSerializer):
    menus = MenuSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    distance = serializers.FloatField(allow_null=True, required=False)
    review_stars = serializers.FloatField(allow_null=True, required=False)
    members_stars = serializers.FloatField(allow_null=True, required=False)

    class Meta:
        model = Store
        fields = '__all__'
