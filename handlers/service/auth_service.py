from telegram import Update,ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
)
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from asgiref.sync import sync_to_async
import re
from apps.accounts.models import User


def normalize_last9(phone: str) -> str:
    digits = re.sub(r"\D", "", phone)
    return digits[-9:]


@sync_to_async
def user_contact_service(user_id: int, phone_number: str):
    user = User.objects.filter(phone__endswith=phone_number).first()

    if not user:
        return None

    user.phone = phone_number
    user.telegram_id = user_id
    user.save(update_fields=["phone", "telegram_id"])
    return user.id


async def get_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact

    if not contact:
        await update.message.reply_text(
            "Iltimos, telefon raqamingizni pasdagi tugma orqali ulashing."
        )
        return

    if contact.user_id != update.message.from_user.id:
        await update.message.reply_text(
            "Iltimos, o'zingizning telefon raqamingizni ulashing."
        )
        return

    phone_number = normalize_last9(contact.phone_number)

    user_id = await user_contact_service(
        user_id=update.message.from_user.id,
        phone_number=phone_number
    )

    if user_id:
        await update.message.reply_text(
            f"✅ Raqamingiz tasdiqlandi: {phone_number}",reply_markup=ReplyKeyboardRemove()
        )
    else:
        await update.message.reply_text(
            "❌ Bu raqam tizimda topilmadi."
        )