from telegram import Update
from telegram.ext import ContextTypes

from ..service import user_status,murojat_comand_service
from apps.applications.serializers import AplicationSendBotSerializers

async def murojat_bot(update:Update,context:ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id


    user = await user_status(telegram_id) 

    data = await murojat_comand_service(user)
    await update.message.reply_text(str(data.data))