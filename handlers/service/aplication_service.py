from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from asgiref.sync import sync_to_async
from django.db import transaction
from django.core.files.base import ContentFile

from apps.accounts.models import User
from apps.applications.models import Application, MahallaReport, Attachment


ASK_COMMENT = 1
ASK_FILE = 2


# =========================
# DB FUNCTIONS
# =========================

@sync_to_async
def get_user(telegram_id):
    return User.objects.filter(telegram_id=telegram_id).first()


@sync_to_async
def update_application_status(application_id, status):
    Application.objects.filter(id=application_id).update(status=status)


@sync_to_async
def save_comment_to_db(application_id, telegram_id, comment, message_id):
    with transaction.atomic():
        user = User.objects.filter(telegram_id=telegram_id).first()

        if not user:
            raise ValueError("User topilmadi")

        Application.objects.filter(id=application_id).update(
            status=Application.Status.INSPECTED
        )

        return MahallaReport.objects.create(
            application_id=application_id,
            oqsoqol=user,
            comment_text=comment,
            telegram_message_id=message_id,
            action_type=MahallaReport.ActionType.COMMENTED,
        )


@sync_to_async
def save_file_to_db(user, application_id, file_bytes, filename, file_type, file_size):
    application = Application.objects.get(id=application_id)

    django_file = ContentFile(file_bytes, name=filename)

    return Attachment.objects.create(
        application=application,
        file=django_file,
        file_type=file_type,
        file_size=file_size,
        uploaded_by=user,
    )


# =========================
# ENTRY HANDLERS
# =========================

async def handle_comment_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    app_id = query.data.split("murojat_comment_")[1]
    context.user_data["app_id"] = app_id

    await query.message.reply_text("✍️ Izoh yozing:")

    return ASK_COMMENT


async def handle_file_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = await get_user(query.from_user.id)

    if not user:
        await query.message.reply_text("❌ User topilmadi")
        return ConversationHandler.END

    app_id = query.data.split("murojat_file_")[1]

    context.user_data["user"] = user
    context.user_data["app_id"] = app_id

    await query.message.reply_text("📎 Rasm yoki fayl yuboring:")

    return ASK_FILE


# =========================
# COMMENT HANDLER
# =========================

async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    app_id = context.user_data.get("app_id")

    if not app_id:
        await update.message.reply_text("❌ Xatolik")
        return ConversationHandler.END

    await save_comment_to_db(
        application_id=app_id,
        telegram_id=update.message.from_user.id,
        comment=text,
        message_id=update.message.message_id,
    )

    await update.message.reply_text("✅ Izoh saqlandi")

    context.user_data.clear()

    return ConversationHandler.END


# =========================
# FILE HANDLER
# =========================

async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app_id = context.user_data.get("app_id")
    user = context.user_data.get("user")

    if not app_id or not user:
        await update.message.reply_text("❌ Xatolik")
        return ConversationHandler.END

    file_bytes = None
    filename = None
    file_type = None
    file_size = None

    # PHOTO
    if update.message.photo:
        photo = update.message.photo[-1]

        tg_file = await photo.get_file()
        file_bytes = await tg_file.download_as_bytearray()

        filename = f"photo_{update.message.message_id}.jpg"
        file_type = "photo"
        file_size = photo.file_size or len(file_bytes)

    # DOCUMENT
    elif update.message.document:
        doc = update.message.document

        tg_file = await doc.get_file()
        file_bytes = await tg_file.download_as_bytearray()

        filename = doc.file_name or f"file_{update.message.message_id}"
        file_type = doc.mime_type or "document"
        file_size = doc.file_size or len(file_bytes)

    else:
        await update.message.reply_text("❌ Fayl yuboring")
        return ASK_FILE

    await save_file_to_db(
        user=user,
        application_id=app_id,
        file_bytes=file_bytes,
        filename=filename,
        file_type=file_type,
        file_size=file_size,
    )
    update_application_status(app_id, Application.Status.INSPECTED)
    await update.message.reply_text("✅ Fayl saqlandi")

    context.user_data.clear()

    return ConversationHandler.END


# =========================
# STATELESS HANDLER
# =========================

async def handle_status_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data

    if data.startswith("murojat_kordim_"):
        app_id = data.split("murojat_kordim_")[1]

        await update_application_status(app_id, Application.Status.ACKNOWLEDGED)

        await query.edit_message_text("✅ Murojat ko‘rildi")

    elif data.startswith("murojat_organdim_"):
        app_id = data.split("murojat_organdim_")[1]

        await update_application_status(app_id, Application.Status.IN_REVIEW)

        await query.edit_message_text("✅ Murojat o‘rganildi")