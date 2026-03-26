from telegram import Update
from telegram.ext import ContextTypes
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from asgiref.sync import sync_to_async

from apps.accounts.models import User
from apps.applications.models import Application

async def aplication_service(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query or update.callback_query
    
    await query.answer()

    query_data = query.data
    await query.edit_message_text("✅ Murojat ko'rdim deb belgilandi.")

    if query_data.startswith("murojat_kordim_"):
        id = query_data.split("murojat_kordim_")[1]
        # Murojatni ko'rdim deb belgilash uchun kerakli kodlar
    elif query_data.startswith("murojat_organdim_"):
        id = query_data.split("murojat_organdim_")[1]
        # Murojatni joyida o'rgandim deb belgilash uchun kerakli kodlar
    elif query_data.startswith("murojat_comment_"):
        id = query_data.split("murojat_comment_")[1]
        # Murojatga izoh qo'shish uchun kerakli kodlar
    elif query_data.startswith("murojat_photo_"):
        id = query_data.split("murojat_photo_")[1]
        # Murojatga rasm yuborish uchun kerakli kodlar
