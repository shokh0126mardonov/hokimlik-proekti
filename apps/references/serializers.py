from rest_framework import serializers

from .models import Mahalla

class MahallaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Mahalla
        fields = "__all__"