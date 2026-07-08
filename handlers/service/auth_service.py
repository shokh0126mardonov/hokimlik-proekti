from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
)
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from asgiref.sync import sync_to_async
import re
from apps.accounts.models import User,Applicant
from handlers.utils import StepAplications

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
            "Iltimos, telefon raqamingizni pastdagi tugma orqali ulashing."
        )
        return  # State o'zgarmaydi, qayta kontakt kutadi

    # 2. Begona raqam yuborilmaganini tekshirish
    if contact.user_id != update.message.from_user.id:
        await update.message.reply_text(
            "Iltimos, o'zingizning telefon raqamingizni ulashing."
        )
        return  # State o'zgarmaydi

    # Kontakt ma'lumotlarini xavfsiz saqlash
    context.user_data['contact'] = contact
    phone_number = normalize_last9(contact.phone_number)
    context.user_data['phone_number'] = phone_number

    telegram_id = update.message.from_user.id

    # Bazadan arizachini tekshirish (Query)
    @sync_to_async
    def check_applicant():
        return Applicant.objects.filter(telegram_id=telegram_id).select_related('mahalla').first()
        
    applicant_exists = await check_applicant()

    if applicant_exists:
        context.user_data['full_name'] = applicant_exists.full_name
        context.user_data['mahalla'] = applicant_exists.mahalla.name if applicant_exists.mahalla else None
        
        # Sifatiy yosh toifasini saqlash
        if applicant_exists.age_medium == '30_plus':
            context.user_data['average_age'] = '30 yoshdan katta'
        else:
            context.user_data['average_age'] = '30 yoshdan kichik'
        
        await update.message.reply_text(
            # f"✅ Raqamingiz tasdiqlandi: {phone_number}\n\n"
            f"✍️ Iltimos, yangi arizangiz yoki murojaatingiz matnini batafsil yozib yuboring:",
            reply_markup=ReplyKeyboardRemove()
        )
        # To'g'ridan-to'g'ri ariza matnini yozish bosqichiga o'tkazamiz
        return StepAplications.TEXT 

    else:
        try:
            await user_contact_service(user_id=telegram_id, phone_number=phone_number)
        except Exception:
            pass # Agar bu xizmat majburiy bo'lmasa yoki xato bersa zanjir uzilib qolmasligi uchun

        await update.message.reply_text(
            # f"✅ Raqamingiz tasdiqlandi: {phone_number}\n\n"
            f"📝 Tizimda topilmadingiz. Iltimos, arizani boshlash uchun familiyangiz, ismingizni to‘liq kiriting:",
            reply_markup=ReplyKeyboardRemove()
        )
        # Ism-familiya so'rash bosqichiga o'tkazamiz
        return StepAplications.FULL_NAME