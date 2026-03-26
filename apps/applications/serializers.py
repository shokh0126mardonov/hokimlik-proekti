import os

from rest_framework import serializers

from apps.references.models import Service
from apps.accounts.models import User
from .models import Application,Attachment,MahallaReport

class AplicationSerializers(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = '__all__'


class SendMahallaSerialisers(serializers.Serializer):
    id = serializers.IntegerField()


class AttachmentSerializers(serializers.Serializer):
    report = serializers.PrimaryKeyRelatedField(
        queryset=MahallaReport.objects.all()
    )
    file = serializers.FileField()

    def create(self, validated_data):
        file_obj = validated_data['file']
        ext = os.path.splitext(file_obj.name)[1].lower()


        return Attachment.objects.create(
            report=validated_data['report'],
            application=validated_data.get('application'),
            uploaded_by=validated_data.get('uploaded_by'),
            file_type = ext ,
            file=file_obj,
            file_size=file_obj.size,  # 🔥 MUHIM
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username','full_name','role']

class AttachmentResponseSerializers(serializers.ModelSerializer):
    uploaded_by = UserSerializer(read_only = True)
    class Meta:
        model = Attachment
        fields = [
            'report','application','file','file_type','file_size','uploaded_by','created_at'
        ]
    

class MahallaRepostSerializers(serializers.ModelSerializer):
    class Meta:
        model = MahallaReport
        fields = '__all__'

    
class AplicationSendBotSerializers(serializers.Serializer):

    app_number = serializers.CharField(max_length=30)
    service = serializers.CharField(source="service.name")  # ✅
    citizen_name = serializers.CharField(max_length = 200)
    address_text = serializers.CharField(max_length=500)

    # class Meta:
    #     model = Application
    #     fields = ['app_number','service','app_type','citizen_name','address_text',"id", "content", "status"]