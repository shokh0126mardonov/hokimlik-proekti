from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import os
import django

from apps.applications.models import  Application, MahallaReport
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from asgiref.sync import sync_to_async

@sync_to_async
def save_comment(app_id, comment, user, message_id):
    report= MahallaReport.objects.create(
            application_id=app_id,
            oqsoqol=user,
            comment_text=comment,
            telegram_message_id=message_id,
            action_type=MahallaReport.ActionType.COMMENTED,
        )   
    Application.objects.filter(id=app_id).update(status=Application.Status.INSPECTED)

    report.save()


async def skip_file_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    app_id = context.user_data.get("app_id")
    user = context.user_data.get("user")
    comment = context.user_data.get("comment")
    message_id = context.user_data.get("message_id")

    await save_comment(app_id, comment, user, message_id)

    await query.edit_message_text("Faylsiz yuborildi ✅")

    return ConversationHandler.END