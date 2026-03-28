import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from asgiref.sync import sync_to_async

from apps.accounts.models import User
from apps.applications.models import Application
from apps.applications.serializers import AplicationSendBotSerializers

@sync_to_async
def murojat_comand_service(user_id: int):
    user = (
        User.objects
        .select_related("mahalla")
        .get(id=user_id)
    )

    qs = (
        Application.objects
        .filter(
            mahalla=user.mahalla,
            status__in=[
                Application.Status.SENT_TO_MAHALLA,
                Application.Status.REOPENED,
                Application.Status.ACKNOWLEDGED
            ]
        )
    )

    # 🔥 GROUPING (MUHIM)
    sent = []
    reopened = []
    acknowledged = []

    for obj in qs:
        if obj.status == Application.Status.SENT_TO_MAHALLA:
            sent.append(obj)
        elif obj.status == Application.Status.REOPENED:
            reopened.append(obj)
        elif obj.status == Application.Status.ACKNOWLEDGED:
            acknowledged.append(obj)

    return {
        "sent": AplicationSendBotSerializers(sent, many=True).data,
        "reopened": AplicationSendBotSerializers(reopened, many=True).data,
        "acknowledged": AplicationSendBotSerializers(acknowledged, many=True).data
    }