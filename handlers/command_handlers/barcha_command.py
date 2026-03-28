from telegram import Update
from telegram.ext import ContextTypes

from handlers.service.user_service import user_status


async def barcha_command_bot(update:Update,context:ContextTypes.DEFAULT_TYPE):
    full_name = update.message.from_user.full_name
    telegram_id = update.message.from_user.id

    user = await user_status(telegram_id) 

    if user:    
        await update.message.reply_text(
            f"Assalomu aleykum {full_name}"
            f"Siznga kelgan barcha arizalaringiz"
        )
