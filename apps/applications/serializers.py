from rest_framework import serializers

from .models import Application,Attachment,MahallaReport

class AplicationSerializers(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = '__all__'


class SendMahallaSerialisers(serializers.Serializer):
    id = serializers.IntegerField()


class AttachmentSerializers(serializers.Serializer):

    report = serializers.PrimaryKeyRelatedField(
        queryset = MahallaReport.objects.all(),
    )

    file = serializers.FileField()

    def create(self, validated_data,**kwargs):
        print(kwargs.get('uploaded_by'))
        return Attachment.objects.create(
                report = validated_data['report'],
                application = kwargs.get('application'),
                file_size = 3,
                uploaded_by = kwargs.get('uploaded_by')
        )

class AttachmentResponseSerializers(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'