from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from asgiref.sync import sync_to_async

from handlers.utils import StepAplications
from apps.applications.models import Application
from apps.references.models import Mahalla
from apps.accounts.models import Applicant

async def get_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi ismini saqlaydi va bazadan mahallalar ro'yxatini chiqaradi"""
    context.user_data['full_name'] = update.message.text
    
    # Bazadan barcha mahallalarni async rejimda olamiz
    @sync_to_async
    def get_all_mahallas():
        return list(Mahalla.objects.values_list('name', flat=True))
    
    mahalla_list = await get_all_mahallas()
    
    if not mahalla_list:
        await update.message.reply_text(
            "Tizimda mahallalar topilmadi. Iltimos, mahalla nomini matn ko'rinishida yozing:"
        )
        return StepAplications.MAHALLA

    # Mahallalarni tugma ko'rinishiga keltiramiz (Qatoriga 2 tadan qilib joylash)
    keyboard = []
    for i in range(0, len(mahalla_list), 2):
        keyboard.append(mahalla_list[i:i+2])
        
    reply_markup = ReplyKeyboardMarkup(
        keyboard, 
        one_time_keyboard=True, 
        resize_keyboard=True
    )
    
    await update.message.reply_text(
        "Rahmat. Endi ro'yxatdan mahallangizni tanlang:",
        reply_markup=reply_markup
    )
    return StepAplications.MAHALLA


async def get_mahalla(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mahallani saqlaydi va yosh toifasini so'raydi"""
    context.user_data['mahalla'] = update.message.text
    
    reply_keyboard = [['30 yoshdan katta', '30 yoshdan kichik']]
    await update.message.reply_text(
        "Yosh toifangizni tanlang:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return StepAplications.AVEREGE_AGE


async def get_average_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yosh toifasini saqlaydi va ariza matnini so'raydi"""
    context.user_data['average_age'] = update.message.text
    await update.message.reply_text(
        "Ariza mazmunini (matnini) batafsil yozing:",
        reply_markup=ReplyKeyboardRemove()
    )
    return StepAplications.TEXT


async def get_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Matnni saqlaydi va barcha ma'lumotlarni tasdiqlash uchun ko'rsatadi"""
    context.user_data['text'] = update.message.text
    
    summary = (
        f"📝 **Ariza ma'lumotlari:**\n\n"
        f"👤 F.I.Sh: {context.user_data['full_name']}\n"
        f"📍 Mahalla: {context.user_data['mahalla']}\n"
        f"⏳ Yosh toifasi: {context.user_data['average_age']}\n"
        f"📄 Matn: {context.user_data['text']}\n\n"
        f"Ma'lumotlar to'g'rimi?"
    )
    reply_keyboard = [['Tasdiqlayman', 'Bekor qilish']]
    await update.message.reply_text(
        summary,
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return StepAplications.CONFIRM

async def confirm_application(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ariza tasdiqlansa ma'lumotlarni yangi Applicant modeliga saqlaydi"""
    answer = update.message.text
    
    if answer == 'Tasdiqlayman':
        # 1. user_data ichidan bot yig'gan barcha ma'lumotlarni olamiz
        full_name = context.user_data.get('full_name')
        mahalla_name = context.user_data.get('mahalla')
        age_text = context.user_data.get('average_age')
        text_content = context.user_data.get('text')
        
        # Foydalanuvchining telegram_id si va kontakt obyekti
        telegram_id = update.message.from_user.id
        contact_obj = context.user_data.get('contact')
        phone_number = contact_obj.phone_number if contact_obj else None

        age_medium = '30_plus' if 'katta' in str(age_text) else '30_minus'

        # 3. Django ORM so'rovini asinxron bajarish uchun ichki funksiya
        @sync_to_async
        def save_applicant_data():
            mahalla_obj = Mahalla.objects.filter(name=mahalla_name).first()
            
            applicant = Applicant.objects.create(
                telegram_id=telegram_id,
                full_name=full_name,
                phone=phone_number,
                mahalla=mahalla_obj,
                age_medium=age_medium,
                text=text_content
            )
            return applicant

        try:
            new_applicant = await save_applicant_data()
            
            app_id = getattr(new_applicant, 'app_number', new_applicant.id)
            
            await update.message.reply_text(
                f"✅ Arizangiz muvaffaqiyatli qabul qilindi!\n\n"
                f"🔢 **Ariza raqamingiz:** #{app_id}\n"
                f"⏳ Arizangiz ko'rib chiqilgach, shu bot orqali sizga javob xati yuboriladi.",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode="Markdown" # Raqamni qalin (bold) ko'rsatish uchun
            )
        except Exception as e:
            await update.message.reply_text(
                "❌ Arizani saqlashda texnik xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                reply_markup=ReplyKeyboardRemove()
            )
            print(f"Applicant saqlashda xato: {e}")
            
    else:
        await update.message.reply_text(
            "Ariza bekor qilindi.", 
            reply_markup=ReplyKeyboardRemove()
        )
    
    # Jarayon tugagach vaqtinchalik ma'lumotlarni o'chiramiz
    context.user_data.clear()
    return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Foydalanuvchi jarayonni bekor qilganda ishlaydi"""
    await update.message.reply_text(
        "Jarayon to'xtatildi.", 
        reply_markup=ReplyKeyboardRemove()
    )
    context.user_data.clear()
    return ConversationHandler.END