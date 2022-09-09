from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer


class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        max_length = 50,
        )
    last_name = serializers.CharField(
        max_length = 50,
        )
    username = serializers.CharField(
        max_length = 50,
        validators = (UniqueValidator(queryset=get_user_model().objects.all()),),
        )
    password = serializers.CharField(
        max_length = 25,
        )

    @staticmethod
    def has_numbers(inputString):
        return any(char.isdigit() for char in inputString)

    def validate_first_name(self, value):
        if self.has_numbers(value):
            raise serializers.ValidationError('first name can not contain digits')
        return value
    
    def validate_last_name(self, value):
        if self.has_numbers(value):
            raise serializers.ValidationError('last name can not contain digits')
        return value
    
    def validate_username(self, value):
        #change this to read from .env or settings
        if len(value) not in range(5, 15):
            raise serializers.ValidationError('username cannot be too long or too short')
        return value
    
    def create(self, validated_data):
        User = get_user_model()
        user = User(
            first_name = validated_data.get("first_name"),
            last_name = validated_data.get("last_name"),
            username = validated_data.get("username"),
        )
        user.set_password(validated_data.get('password'))
        user.save()
        return user
