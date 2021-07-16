from rest_framework import serializers
from .models import Store, Category, Menu


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['store', 'name', 'price', 'image_url', 'id']

    def get_image_url(self, queryset):
        request = self.context.get('request')
        if queryset.image:
            image_url = queryset.image.url
            return request.build_absolute_uri(image_url)
        return None


class StoreSerializer(serializers.ModelSerializer):
    menus = MenuSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    distance = serializers.FloatField(allow_null=True)
    review_stars = serializers.FloatField(allow_null=True)

    class Meta:
        model = Store
        fields = '__all__'
