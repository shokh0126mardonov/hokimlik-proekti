from telegram import Bot
from decouple import config
from telegram.constants import ParseMode
TOKEN = config("TOKEN")


async def bot_send_message(chat_id: int, status: str):
    bot = Bot(token=TOKEN)

    if status == "reopened":
        text = (
            "🔄 <b>ARIZA QAYTA OCHILDI</b>\n"
            "────────────────────────\n\n"
            "📌 <b>Status:</b> Qayta ochildi\n"
            "📊 <b>Holat:</b> Qayta ko‘rib chiqish talab etiladi\n\n"
            "⚠️ <i>Arizani qayta ko‘rish uchun /murojatlar buyrug‘idan foydalaning.</i>"
        )

    elif status == "sent_to_mahalla":
        text = (
            "📤 <b>ARIZA MAHALLAGA YUBORILDI</b>\n"
            "────────────────────────\n\n"
            "📌 <b>Status:</b> Mahallaga yuborildi\n"
            "📊 <b>Holat:</b> Mahalla tomonidan ko‘rib chiqilmoqda\n\n"
            "ℹ️ <i>Arizani ko‘rish uchun /murojatlar buyrug‘idan foydalaning.</i>"
        )
    await bot.send_message(chat_id=chat_id, text=text, parse_mode="HTML")

from telegram import Bot
from telegram.constants import ParseMode


async def send_response_to_telegram(applicant, file=None):
    """
    Applicant obyektini qabul qilib, uning telegram_id siga 
    yozilgan javobni (response) yuboradi.
    """
    bot = Bot(token=TOKEN)
    
    if not applicant.response:
        return

    text = (
        f"🔔 **Arizangiz bo'yicha javob xati:**\n\n"
        f"👤 **Kimdan:** Hokimlik va mahalla boshqarmasi\n"
        f"📝 **Sizning arizangiz raqami:** {applicant.app_number}...\n"
        f"✉️ **Javob:** {applicant.response}"
    )

    try:
        if file:
            await bot.send_document(
                chat_id=applicant.telegram_id,
                document=file,
                caption=text,
                parse_mode=ParseMode.MARKDOWN 
            )
        else:
            await bot.send_message(
                chat_id=applicant.telegram_id,
                text=text,
                parse_mode=ParseMode.MARKDOWN
            )
        print(f"Javob {applicant.full_name} ga (ID: {applicant.telegram_id}) yuborildi.")
        
    except Exception as e:
        print(f"Telegramga xabar yuborishda xatolik: {e}")