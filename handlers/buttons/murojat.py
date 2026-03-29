from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def murojat_organdim_button(id):
    keyboard = [
        [InlineKeyboardButton("izoh qo'shish", callback_data=f"murojat_organdim_{id}")]
    ]
    return InlineKeyboardMarkup(keyboard)

def murojat_button(id):
    keyboard = [
        [InlineKeyboardButton("✅ Batafsil ko'rish", callback_data=f"murojat_kordim_{id}")],
        [InlineKeyboardButton("🔍 Joyida o'rgandim", callback_data=f"murojat_organdim_{id}")],

    ]
    return InlineKeyboardMarkup(keyboard)

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def skip_file_button():
    keyboard = [
        [InlineKeyboardButton("⏭ Skip", callback_data="skip_file")]
    ]
    return InlineKeyboardMarkup(keyboard)
