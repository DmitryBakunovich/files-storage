from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_jwt.settings import api_settings

from .models import CustomUser, Folder, File

JWT_PAYLOAD_HANDLER = api_settings.JWT_PAYLOAD_HANDLER
JWT_ENCODE_HANDLER = api_settings.JWT_ENCODE_HANDLER


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):
        user = authenticate(
            username=data.get('username'),
            password=data.get('password')
        )
        if user is None:
            raise serializers.ValidationError(
                'A user with this username and password is not found'
            )
        try:
            payload = JWT_PAYLOAD_HANDLER(user)
            jwt_token = JWT_ENCODE_HANDLER(payload)
            update_last_login(None, user)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                'User with given username and password does not exists'
            )
        return {
            'username': user.username,
            'token': jwt_token
        }


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'password2',
        )
        read_only_fields = (
            'id',
        )
        extra_kwargs = {
            'password': {
                'max_length': 128,
                'min_length': 8,
                'write_only': True,
            }
        }

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )

        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError(
                {'password': 'Passwords do not match.'}
            )
        user.set_password(password)
        user.save()

        # Create user folder
        Folder.objects.create(
            parent=None,
            name=user.username,
            owner=user
        )
        return user


class FolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Folder
        fields = (
            'id',
            'name',
        )
        read_only_fields = (
            'id',
        )


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = (
            'id',
            'name',
            'created',
            'owner'
        )
        read_only_fields = (
            'id',
        )
