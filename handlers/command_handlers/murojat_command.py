from telegram import Update
from telegram.ext import ContextTypes

from ..service import user_status, murojat_comand_service


async def murojat_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id

    user = await user_status(telegram_id)

    if not user:
        await update.message.reply_text("Sizga ruxsat yo‘q")
        return

    data = await murojat_comand_service(user.id)

    if not data:
        await update.message.reply_text("Murojatlar topilmadi")
        return

    message = "\n\n".join(
        f"<b>📄 Ariza:</b> #{item.get('app_number')}\n"
        f"<b>🏢 Xizmat:</b> {item.get('service')}\n"
        f"<b>👤 Fuqaro:</b> {item.get('citizen_name')}\n"
        f"<b>📍 Manzil:</b> {item.get('address_text')}"
        for item in data
    )

    await update.message.reply_text(message, parse_mode="HTML")