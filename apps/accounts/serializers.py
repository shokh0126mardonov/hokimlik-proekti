from django.contrib.auth import get_user_model

from rest_framework import serializers

# User = get_user_model()
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "role",
            "first_name",
            "last_name",
            "email",
            "full_name",
            "phone",
            "telegram_id",
            "created_at",
            "service",
            "mahalla",
        ]


class RegisterSerializers(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=200)
    role = serializers.ChoiceField(
        choices=[
            User.Role.SUPER_ADMIN,
            User.Role.HOKIM,
            User.Role.OQSOQOL,
            User.Role.SERVICE_STAFF,
        ]
    )

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "full_name",
            "role",
            "email",
            "phone",
            "telegram_id",
            "created_at",
            "service",
            "mahalla",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.set_password(password)
        user.save()

        return user


class OqsoqolAddSerializers(serializers.Serializer):
    file = serializers.FileField()
