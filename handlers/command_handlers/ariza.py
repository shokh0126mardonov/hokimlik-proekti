import os
import django
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

# Django muhitini yuklash
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from handlers.utils import StepAplications
from apps.accounts.models import Applicant

async def ariza_yuborish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """ Foydalanuvchi /ariza buyrug'ini bosganda ishlaydi """
    user_id = update.effective_user.id

    applicant = await Applicant.objects.filter(telegram_id=user_id).select_related('mahalla').afirst()

    if applicant:
        context.user_data['full_name'] = applicant.full_name
        context.user_data['mahalla'] = applicant.mahalla.name if applicant.mahalla else "Ko'rsatilmagan"
        context.user_data['average_age'] = '30 yoshdan katta' if applicant.age_medium == '30_plus' else '30 yoshdan kichik'
        context.user_data['phone_number'] = applicant.phone

        await update.message.reply_text(
            "✍️ Arizangiz yoki murojaatingiz matnini batafsil yozib yuboring:",
            reply_markup=ReplyKeyboardRemove()
        )
        return StepAplications.TEXT

    await update.message.reply_text(
        "❌ Siz hali ro'yxatdan o'tmagansiz!\n\n"
        "Iltimos, avval /start buyrug'i orqali ro'yxatdan o'ting.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END