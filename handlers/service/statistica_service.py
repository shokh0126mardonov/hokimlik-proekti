from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


from asgiref.sync import sync_to_async

from apps.applications.models import Application


@sync_to_async
def statistic_service(status=None, mahalla=None):
    queryset = Application.objects.all()

    if status:
        queryset = queryset.filter(status=status)

    if mahalla:
        queryset = queryset.filter(mahalla=mahalla)

    return queryset.count()
