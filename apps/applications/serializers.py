from rest_framework import serializers

from .models import Application

class AplicationSerializers(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = '__all__'


class SendMahallaSerialisers(serializers.Serializer):
    id = serializers.IntegerField()