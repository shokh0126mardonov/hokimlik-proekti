from telegram import Update
from telegram.ext import ContextTypes


async def help_command_bot(update:Update,context:ContextTypes.DEFAULT_TYPE):
    full_name = update.message.from_user.full_name

    await update.message.reply_text(
        f"Assalomu aleykum {full_name}"
    )
