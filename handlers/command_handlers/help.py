from telegram import Update
from telegram.ext import ContextTypes

from handlers.service.user_service import user_status


async def help_command_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    full_name = update.message.from_user.full_name

    telegram_id = update.message.from_user.id
    user = await user_status(telegram_id)

    if user:
        from html import escape

        await update.message.reply_text(
            f"<b>Assalomu alaykum, {escape(user.full_name)}!</b>\n\n"
            f"<b>Tizimdan foydalanish bo‘yicha buyruqlar:</b>\n\n"
            f"▪ /start\n"
            f"  Botni ishga tushirish\n\n"
            f"▪ /murojatlar\n"
            f"  Yangi murojaatlarni ko‘rish\n\n"
            # f"▪ /barcha\n"
            # f"  Barcha murojaatlar ro‘yxati\n\n"
            f"▪ /statistika\n"
            f"  Statistik ma’lumotlarni ko‘rish\n\n"
            f"▪ /yordam\n"
            f"  Yordam bo‘limi\n\n"
            f"<i>Tegishli buyruqni tanlab, yuborish orqali davom eting.</i>",
            parse_mode="HTML",
        )
