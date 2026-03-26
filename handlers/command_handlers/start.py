from telegram import Update
from telegram.ext import ContextTypes

from ..service import user_status


async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id
    full_name = update.message.from_user.full_name

    user = await user_status(telegram_id) 

    if user:
        await update.message.reply_text(f"Assalomu aleykum {full_name}")
    else:
        await update.message.reply_text("Siz oqsoqol emassiz")
