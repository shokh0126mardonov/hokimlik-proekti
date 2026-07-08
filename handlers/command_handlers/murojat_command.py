from telegram import Update
from telegram.ext import ContextTypes
import html

from ..buttons.murojat import murojat_button, murojat_organdim_button
from ..service import user_status, murojat_comand_service


async def murojat_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = update.message.from_user.id

    user = await user_status(telegram_id)

    # ✅ FIX 1
    if user:
        data = await murojat_comand_service(user.id)

        sent = data.get("sent", [])
        reopened = data.get("reopened", [])
        acknowledged = data.get("acknowledged", [])

        # ✅ FIX 2
        if not sent and not reopened and not acknowledged:
            await update.message.reply_text("📭 Murojatlar topilmadi")
            return

        # =========================
        # SENT
        # =========================
        if sent:
            await update.message.reply_text(
                "📨 <b>Yangi murojaatlar</b>", parse_mode="HTML"
            )

            for item in sent:
                app_number = str(item.get("app_number") or "")
                service = html.escape(str(item.get("service") or ""))
                citizen_name = html.escape(str(item.get("citizen_name") or ""))
                address_text = html.escape(str(item.get("address_text") or ""))

                message = (
                    f"<b>📄 Ariza:</b> #{app_number}\n"
                    f"<b>🏢 Xizmat:</b> {service}\n"
                    f"<b>👤 Fuqaro:</b> {citizen_name}\n"
                    f"<b>📍 Manzil:</b> {address_text}"
                )

                await update.message.reply_text(
                    message,
                    reply_markup=murojat_button(item.get("id")),
                    parse_mode="HTML",
                )

        # =========================
        # REOPENED
        # =========================
        if reopened:
            await update.message.reply_text(
                "♻️ <b>Qayta ochilgan murojaatlar</b>", parse_mode="HTML"
            )

            for item in reopened:
                app_number = str(item.get("app_number") or "")
                service = html.escape(str(item.get("service") or ""))
                citizen_name = html.escape(str(item.get("citizen_name") or ""))
                address_text = html.escape(str(item.get("address_text") or ""))

                message = (
                    f"<b>📄 Ariza:</b> #{app_number}\n"
                    f"<b>🏢 Xizmat:</b> {service}\n"
                    f"<b>👤 Fuqaro:</b> {citizen_name}\n"
                    f"<b>📍 Manzil:</b> {address_text}"
                )

                await update.message.reply_text(
                    message,
                    reply_markup=murojat_button(item.get("id")),
                    parse_mode="HTML",
                )
        # =========================
        # ACKNOWLEDGED
        # =========================
        if acknowledged:
            await update.message.reply_text(
                "✅ <b>Ko'rilgan murojaatlar</b>", parse_mode="HTML"
            )

            for item in acknowledged:
                app_number = str(item.get("app_number") or "")
                service = html.escape(str(item.get("service") or ""))
                citizen_name = html.escape(str(item.get("citizen_name") or ""))
                address_text = html.escape(str(item.get("address_text") or ""))

                message = (
                    f"<b>📄 Ariza:</b> #{app_number}\n"
                    f"<b>🏢 Xizmat:</b> {service}\n"
                    f"<b>👤 Fuqaro:</b> {citizen_name}\n"
                    f"<b>📍 Manzil:</b> {address_text}"
                )

                await update.message.reply_text(
                    message,
                    reply_markup=murojat_organdim_button(item.get("id")),
                    parse_mode="HTML",
                )
