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


from rest_framework import serializers
from .models import Applicant
# Agar Mahalla serializerini ham chiqarmoqchi bo'lsangiz:
# from apps.references.serializers import MahallaSerializer 

class ApplicantSerializer(serializers.ModelSerializer):
    mahalla_name = serializers.CharField(source='mahalla.name', read_only=True)
    
    age_medium_display = serializers.CharField(source='get_age_medium_display', read_only=True)

    class Meta:
        model = Applicant
        fields = [
            'id', 
            'full_name', 
            'phone', 
            'age_medium', 
            'age_medium_display',
            'mahalla', 
            'mahalla_name', 
            'text', 
            'response'
        ]
        
        extra_kwargs = {
            'response': {'required': False, 'allow_blank': True}
        }

from rest_framework import serializers
from .models import Applicant

class ApplicantSerializer(serializers.ModelSerializer):
    """Faqat ma'lumotlarni o'qish (GET) uchun serializer"""
    mahalla_name = serializers.CharField(source='mahalla.name', read_only=True)
    age_medium_display = serializers.CharField(source='get_age_medium_display', read_only=True)

    class Meta:
        model = Applicant
        fields = ['id', 'full_name', 'phone', 'age_medium', 'age_medium_display', 'mahalla', 'mahalla_name', 'text', 'response']


class ApplicantResponseUpdateSerializer(serializers.ModelSerializer):
    """Faqat 'response' fieldiga yozish (PATCH/PUT) uchun serializer"""
    class Meta:
        model = Applicant
        fields = ['response'] # Faqat shu maydon Swaggerda ochiladi, qolganlari yopiladi