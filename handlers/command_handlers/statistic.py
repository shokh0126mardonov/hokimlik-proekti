from telegram import Update
from telegram.ext import ContextTypes

from handlers.service.user_service import user_status
from handlers.service.statistica_service import statistic_service


async def statistic_command_bot(update:Update,context:ContextTypes.DEFAULT_TYPE):
    full_name = update.message.from_user.full_name
    telegram_id = update.message.from_user.id

    user = await user_status(telegram_id) 
    if user:
        await update.message.reply_text(
            f"<b>📊 MUROJATLAR STATISTIKASI</b>\n"
            f"━━━━━━━━━━━━━━━━━━━\n\n"

            f"📦 <b>Jami murojaatlar:</b>\n"
            f"   └ {await statistic_service(mahalla=user.mahalla)}\n\n"

            f"🆕 <b>Yangi murojaatlar:</b>\n"
            f"   └ {await statistic_service(mahalla=user.mahalla, status='new')}\n\n"

            f"📨 <b>Mahallaga biriktirilgan:</b>\n"
            f"   └ {await statistic_service(mahalla=user.mahalla, status='sent_to_mahalla')}\n\n"

            f"✅ <b>Qabul qilingan:</b>\n"
            f"   └ {await statistic_service(mahalla=user.mahalla, status='acknowledged')}\n\n"

            f"🔍 <b>Tekshirilgan:</b>\n"
            f"   └ {await statistic_service(mahalla=user.mahalla, status='inspected')}\n\n"

            f"🔒 <b>Yopilgan:</b>\n"
            f"   └ {await statistic_service(mahalla=user.mahalla, status='closed')}\n\n"

            f"━━━━━━━━━━━━━━━━━━━\n"
            f"<i>📌 Ma'lumotlar real vaqt rejimida yangilanadi</i>",
            parse_mode="HTML"
        )

