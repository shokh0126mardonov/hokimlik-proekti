from telegram import Update
from telegram.ext import ContextTypes

from ..service import user_status


async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    full_name = update.message.from_user.full_name

    user = await user_status(telegram_id) 

    if user:
        await update.message.reply_text(
            f"👋 <b>Assalomu alaykum, {user.full_name}!</b>\n\n"
            f"🏡 Siz <strong>{user.mahalla}</strong> mahallasining oqsoqoli sifatida "
            f"<i>tizimga muvaffaqiyatli kirdingiz</i>.\n\n"
            f"✨ <u>Sizga muvaffaqiyatli ish kuni tilaymiz!</u>",
            parse_mode="HTML"
        )
    # else:
    #     await update.message.reply_text("Siz oqsoqol emassiz")
