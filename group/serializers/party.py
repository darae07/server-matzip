from django.db.models import Count
from rest_framework import serializers

from group.models_party import Party
from group.serializer import MembershipSerializer


class PartyListSerializer(serializers.ModelSerializer):
    membership = MembershipSerializer(read_only=True, many=True)

    class Meta:
        model = Party
        fields = '__all__'


class PartyDetailSerializer(serializers.ModelSerializer):
    membership = MembershipSerializer(read_only=True, many=True)

    class Meta:
        model = Party
        fields = '__all__'


class PartySerializer(serializers.ModelSerializer):

    class Meta:
        model = Party
        fields = '__all__'
        list_serializer_class = PartyListSerializer
