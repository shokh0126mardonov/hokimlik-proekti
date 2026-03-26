from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def murojat_button(id):
    keyboard = [
        [InlineKeyboardButton("✅ Ko'rdim", callback_data=f"murojat_{id}")],
        [InlineKeyboardButton("🔍 Joyida o'rgandim", callback_data=f"murojat_no_{id}")],
        [InlineKeyboardButton("💬 Izoh qo'shish", callback_data=f"murojat_comment_{id}")],
        [InlineKeyboardButton("📷 Rasm yuborish", callback_data=f"murojat_reject_{id}")]

    ]
    return InlineKeyboardMarkup(keyboard)
