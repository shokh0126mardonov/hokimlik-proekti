from telegram import Update
from telegram.ext import ContextTypes
import html

from ..buttons.murojat import murojat_button
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

    for item in data:
        
        app_number = str(item.get('app_number') or '')
        service = html.escape(str(item.get('service') or ''))
        citizen_name = html.escape(str(item.get('citizen_name') or ''))
        address_text = html.escape(str(item.get('address_text') or ''))

        message = (f"<b>📄 Ariza:</b> #{app_number}\n"
            f"<b>🏢 Xizmat:</b> {service}\n"
            f"<b>👤 Fuqaro:</b> {citizen_name}\n"
            f"<b>📍 Manzil:</b> {address_text}"
            )
        await update.message.reply_text(message,reply_markup=murojat_button(item.get('id')), parse_mode="HTML")
