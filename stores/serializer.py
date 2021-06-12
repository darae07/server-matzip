from rest_framework import serializers
from .models import Store, Dong, Category, Menu


class DongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dong
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['menu_name', 'price', 'image_url']

    def get_image_url(self, queryset):
        request = self.context.get('request')
        image_url = queryset.image.url
        return request.build_absolute_uri(image_url)


class StoreSerializer(serializers.ModelSerializer):
    menus = MenuSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    dong = DongSerializer(read_only=True)

    class Meta:
        model = Store
        fields = '__all__'
