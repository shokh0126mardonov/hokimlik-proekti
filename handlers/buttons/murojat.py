from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def murojat_button(id):
    keyboard = [
        [InlineKeyboardButton("✅ Ko'rdim", callback_data=f"murojat_kordim_{id}")],
        [InlineKeyboardButton("🔍 Joyida o'rgandim", callback_data=f"murojat_organdim_{id}")],
        [InlineKeyboardButton("💬 Izoh qo'shish", callback_data=f"murojat_comment_{id}")],
        [InlineKeyboardButton("📷 Rasm yuborish", callback_data=f"murojat_file_{id}")]

    ]
    return InlineKeyboardMarkup(keyboard)
