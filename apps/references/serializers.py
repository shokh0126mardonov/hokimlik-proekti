from rest_framework import serializers

from .models import Mahalla, Service, ApplicationType


class MahallaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Mahalla
        fields = "__all__"


class ServiceSerializers(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = "__all__"


class ApplicationTypeSerializers(serializers.ModelSerializer):
    class Meta:
        model = ApplicationType
        fields = "__all__"
