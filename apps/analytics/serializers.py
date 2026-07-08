from rest_framework import serializers


class KunlikStatSerializer(serializers.Serializer):
    sana = serializers.DateField(source="date")
    soni = serializers.IntegerField(source="count")


class PrognozSerializer(serializers.Serializer):
    sana = serializers.DateField(source="ds")
    kutilayotgan_soni = serializers.FloatField(source="yhat")


class AnalyticsSerializer(serializers.Serializer):
    jami_arizalar = serializers.IntegerField(source="total")
    yopilgan_arizalar = serializers.IntegerField(source="closed")
    kutilayotgan_arizalar = serializers.IntegerField(source="pending")
    rad_etilgan_arizalar = serializers.IntegerField(source="rejected")

    ortacha_javob_vaqti = serializers.DurationField(source="avg_response_time", allow_null=True)

    kunlik_statistika = KunlikStatSerializer(source="trend", many=True)
    prognoz = PrognozSerializer(source="forecast", many=True)

    tahlil_xulosasi = serializers.CharField(source="insight")
    muammo_tahlili = serializers.CharField(source="bottleneck")