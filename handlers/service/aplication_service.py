from email.mime import application

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from asgiref.sync import sync_to_async

from apps.accounts.models import User
from apps.applications.models import Application,MahallaReport


ASK_COMMENT = 1

@sync_to_async
def save_comment_to_db(application_id, telegram_id, comment):
    user = User.objects.filter(telegram_id=telegram_id).first()

    if not user:
        raise ValueError("User topilmadi")

    return MahallaReport.objects.create(
        application_id=application_id,
        oqsoqol=user,
        comment_text=comment
    )



async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    app_id = context.user_data.get("comment_app_id")

    if not app_id:
        await update.message.reply_text("❌ Xatolik. Qaytadan urinib ko‘ring.")
        return ConversationHandler.END

    telegram_id = update.message.from_user.id

    await save_comment_to_db(app_id, telegram_id, text)

    await update.message.reply_text("✅ Izoh saqlandi")

    context.user_data.pop("comment_app_id", None)

    return ConversationHandler.END


@sync_to_async
def aplication_update_status(application_id, status):
    application = Application.objects.get(id=application_id)
    application.status = status
    application.save()



async def aplication_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query or update.callback_query
    
    await query.answer()

    query_data = query.data

    if query_data.startswith("murojat_kordim_"):
        id = query_data.split("murojat_kordim_")[1]
        await aplication_update_status(id, Application.Status.ACKNOWLEDGED)
        await query.edit_message_text("✅ Murojat ko'rdim deb belgilandi.")

    elif query_data.startswith("murojat_organdim_"):
        id = query_data.split("murojat_organdim_")[1]
        await aplication_update_status(id, Application.Status.IN_REVIEW)
        await query.edit_message_text("✅ Murojat joyida o'rgandim deb belgilandi.")

    elif query_data.startswith("murojat_comment_"):
        id = query_data.split("murojat_comment_")[1]

        context.user_data["comment_app_id"] = id
        await query.message.reply_text("✍️ Iltimos, izoh yozing:")

        return ASK_COMMENT

    elif query_data.startswith("murojat_photo_"):
        id = query_data.split("murojat_photo_")[1]
        # Murojatga rasm yuborish uchun kerakli kodlar

