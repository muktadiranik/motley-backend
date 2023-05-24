from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["email"] = self.user.email
        data["phone"] = self.user.phone
        data["first_name"] = self.user.first_name
        data["last_name"] = self.user.last_name
        data["is_superuser"] = self.user.is_superuser
        data["is_staff"] = self.user.is_staff

        return data


class UserSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "refresh", "access",
                  "email", "password", "first_name", "last_name", "phone", "is_superuser", "is_staff"]

    def get_access(self, user):
        token = RefreshToken.for_user(user)
        return str(token.access_token)

    def get_refresh(self, user):
        token = RefreshToken.for_user(user)
        return str(token)


class CreateUserSerializer(ModelSerializer):
    id = serializers.ReadOnlyField()
    access = serializers.SerializerMethodField(read_only=True)
    refresh = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ["id", "refresh", "access",
                  "email", "password", "first_name", "last_name", "phone", "is_superuser", "is_staff"]

    def get_access(self, user):
        token = RefreshToken.for_user(user)
        return str(token.access_token)

    def get_refresh(self, user):
        token = RefreshToken.for_user(user)
        return str(token)

    def save(self, **kwargs):
        email = self.validated_data["email"]
        first_name = self.validated_data["first_name"]
        last_name = self.validated_data["last_name"]
        phone = self.validated_data["phone"]
        password = make_password(self.validated_data["password"])
        self.instance = User.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            is_superuser=False,
            is_staff=False,
        )
        return self.instance
