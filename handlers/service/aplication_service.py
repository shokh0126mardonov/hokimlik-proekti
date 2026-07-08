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
from apps.applications.serializers import AplicationSendBotSerializers
from ..buttons.murojat import murojat_organdim_button
from ..buttons.murojat import skip_file_button

# STATES
ASK_COMMENT = 1
ASK_FILE = 2


# =========================
# DB HELPERS
# =========================


@sync_to_async
def get_application(app_id):
    return Application.objects.get(id=app_id)


@sync_to_async
def get_user(telegram_id):
    return User.objects.filter(telegram_id=telegram_id).first()


@sync_to_async
def update_application_status(application_id, status):
    Application.objects.filter(id=application_id).update(status=status)


# =========================
# ENTRY POINT
# =========================


async def handle_status_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data or ""

    # KO‘RDIM
    if data.startswith("murojat_kordim_"):
        try:
            app_id = data.split("murojat_kordim_")[1]
        except IndexError:
            await query.message.reply_text("❌ Xatolik")
            return ConversationHandler.END

        aplication = await get_application(app_id)
        data = AplicationSendBotSerializers(aplication).data
        message = (
            f"<b>📄 Ariza №:</b> #{data.get('app_number')}\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 <b>Murojaat turi:</b>\n"
            f"{data.get('content')}\n\n"
            f"👤 <b>Fuqaro:</b>\n"
            f"{data.get('citizen_name')}\n\n"
            f"📞 <b>Telefon:</b>\n"
            f"{data.get('citizen_phone') or '—'}\n\n"
            f"📍 <b>Manzil:</b>\n"
            f"{data.get('address_text')}\n\n"
            f"⏳ <b>Muddati:</b>\n"
            f"{data.get('deadline') or '—'}\n\n"
            f"🕒 <b>Yaratilgan sana:</b>\n"
            f"{data.get('created_at')}\n\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<i>📌 Iltimos, murojaatni ko‘rib chiqing</i>"
        )

        await query.edit_message_text(
            message,
            reply_markup=murojat_organdim_button(app_id),
            parse_mode="HTML",
        )
        await update_application_status(app_id, Application.Status.ACKNOWLEDGED)

        return ConversationHandler.END

    # O‘RGANDIM → FLOW
    elif data.startswith("murojat_organdim_"):
        try:
            app_id = data.split("murojat_organdim_")[1]
        except IndexError:
            await query.message.reply_text("❌ Xatolik")
            return ConversationHandler.END

        user = await get_user(query.from_user.id)
        if not user:
            await query.message.reply_text("❌ User topilmadi")
            return ConversationHandler.END

        context.user_data.clear()
        context.user_data["app_id"] = app_id
        context.user_data["user"] = user

        # await update_application_status(app_id, Application.Status.IN_REVIEW)

        await query.message.reply_text("✍️ Izoh yozing:")

        return ASK_COMMENT

    return ConversationHandler.END


# =========================
# COMMENT STEP
# =========================


async def save_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        await update.message.reply_text("❌ Matn yuboring")
        return ASK_COMMENT

    app_id = context.user_data.get("app_id")
    user = context.user_data.get("user")

    if not app_id or not user:
        await update.message.reply_text("❌ Xatolik")
        return ConversationHandler.END

    context.user_data["comment"] = update.message.text.strip()
    context.user_data["message_id"] = update.message.message_id

    await update.message.reply_text(
        "📎 Endi fayl yuboring:", reply_markup=skip_file_button()
    )

    return ASK_FILE


# =========================
# FILE STEP + FINAL SAVE
# =========================


async def handle_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    app_id = context.user_data.get("app_id")
    user = context.user_data.get("user")
    comment = context.user_data.get("comment")
    message_id = context.user_data.get("message_id")

    if not all([app_id, user, comment]):
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

    @sync_to_async
    def save_all():
        with transaction.atomic():
            report = MahallaReport.objects.create(
                application_id=app_id,
                oqsoqol=user,
                comment_text=comment,
                telegram_message_id=message_id,
                action_type=MahallaReport.ActionType.COMMENTED,
            )

            django_file = ContentFile(file_bytes, name=filename)

            Attachment.objects.create(
                report=report,
                application_id=app_id,
                file=django_file,
                file_type=file_type,
                file_size=file_size,
                uploaded_by=user,
            )

            Application.objects.filter(id=app_id).update(
                status=Application.Status.INSPECTED
            )

    await save_all()

    await update.message.reply_text("✅ Izoh va fayl saqlandi")

    context.user_data.clear()

    return ConversationHandler.END
