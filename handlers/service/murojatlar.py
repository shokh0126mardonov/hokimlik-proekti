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
    """
    Full sync boundary:
    - user fetch
    - related loading
    - queryset execution
    - serialization
    """

    user = (
        User.objects
        .select_related("mahalla")  # lazy load oldini oladi
        .get(id=user_id)
    )

    qs = (
        Application.objects
        .filter(mahalla=user.mahalla,
        status = Application.Status.SENT_TO_MAHALLA
        )
        # agar FK lar bo‘lsa qo‘sh:
        # .select_related("field1")
        # .prefetch_related("field2")
    )

    # 🔥 ENG MUHIM JOY
    return AplicationSendBotSerializers(qs, many=True).data