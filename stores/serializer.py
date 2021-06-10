from rest_framework import serializers
from .models import Store, Dong, Category


class StoreSerializer(serializers.ModelSerializer):
    menus = serializers.StringRelatedField(many=True)

    class Meta:
        model = Store
        fields = ('name', 'dong', 'category', 'menus')


class DongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dong
        fields = ['name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name']