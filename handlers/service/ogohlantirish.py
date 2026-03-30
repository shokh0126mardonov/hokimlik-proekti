from telegram import Bot
from decouple import config

TOKEN = config("TOKEN")


async def bot_send_message(chat_id: int, status: str):
    bot = Bot(token=TOKEN)

    if status == "new":
        text = (
            "📩 <b>YANGI ARIZA QABUL QILINDI</b>\n"
            "────────────────────────\n\n"
            
            "📌 <b>Status:</b> Yangi\n"
            "📊 <b>Holat:</b> Ko‘rib chiqilmoqda\n\n"
            
            "ℹ️ <i>Arizani mahallangizga biriktirilgandan keyin sizga xabar beriladi</i>"
        )

    elif status == "reopen":
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
    await bot.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode="HTML"
    )