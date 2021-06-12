from rest_framework import serializers
from .models import Store, Dong, Category, Menu


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


class MenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['menu_name', 'price', 'image_url']

    def get_image_url(self, queryset):
        request = self.context.get('request')
        image_url = queryset.image.url
        return request.build_absolute_uri(image_url)