from rest_framework import serializers
from .models import UserDetails


class ass_serial(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = '__all__'


class User_email(serializers.Serializer):
    user_email = serializers.CharField()