from rest_framework import serializers
from group.models_team import TeamMember
from group.serializers.team_member import TeamMemberSerializer
from .models import CommonUser, ResetPasswordCode


class LoginSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)
    team_profile = serializers.SerializerMethodField('get_team_profile')

    def get_team_profile(self, instance):
        user = instance.id
        my_membership = TeamMember.objects.filter(user=user).order_by('-is_selected').first()
        if my_membership:
            serializer = TeamMemberSerializer(my_membership)
            return serializer.data
        return None

    class Meta:
        model = CommonUser
        fields = ['id', 'email', 'last_login', 'is_superuser', 'is_staff',
                  'date_joined', 'nickname', 'image', 'status', 'phone_number', 'team_profile', 'login_method']


class UserSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = CommonUser
        fields = ['id', 'email', 'last_login',
                  'date_joined', 'nickname', 'image', 'status', 'phone_number']


class AuthenticatedUserSerializer(UserSerializer):
    team_profile = serializers.SerializerMethodField('get_team_profile')

    def get_team_profile(self, instance):
        if instance.team_membership:
            my_membership = instance.team_membership.order_by('-is_selected').first()
            serializer = TeamMemberSerializer(my_membership)
            return serializer.data
        return None

    class Meta:
        fields = ['id', 'email', 'last_login',
                  'date_joined', 'nickname', 'image', 'status', 'phone_number', 'team_profile']


class ResetPasswordCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResetPasswordCode
        fields = '__all__'
