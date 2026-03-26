import os
import django
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

django.setup()

from asgiref.sync import sync_to_async

from apps.applications.serializers import AplicationSendBotSerializers


from apps.accounts.models import User
from apps.applications.models import Application

@sync_to_async
def murojat_comand_service(user:User):
    data = Application.objects.filter(mahalla = user.mahalla).all()
    return AplicationSendBotSerializers(data,many=True)
    


