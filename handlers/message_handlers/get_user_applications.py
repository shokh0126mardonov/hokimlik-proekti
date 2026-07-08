from telegram import Update, ReplyKeyboardRemove, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from asgiref.sync import sync_to_async

from handlers.utils import StepAplications
from apps.applications.models import Application
from apps.references.models import Mahalla


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
    """Ariza tasdiqlansa bazaga saqlaydi, aks holda bekor qiladi"""
    answer = update.message.text
    
    if answer == 'Tasdiqlayman':
        # user_data ichidan bot yig'gan barcha ma'lumotlarni olamiz
        full_name = context.user_data.get('full_name')
        mahalla_name = context.user_data.get('mahalla')
        age_text = context.user_data.get('average_age')
        text_content = context.user_data.get('text')
        
        # get_contact qadamida olingan kontakt obyekti
        contact_obj = context.user_data.get('contact')
        phone_number = contact_obj.phone_number if contact_obj else None

        # Yosh toifasini model variantlariga moslaymiz ('30_plus' yoki '30_minus')
        age_medium = '30_plus' if 'katta' in str(age_text) else '30_minus'

        # Django ORM so'rovini asinxron bajarish uchun ichki funksiya
        @sync_to_async
        def save_application():
            # Tanlangan nom bo'yicha mahalla obyektini topamiz
            mahalla_obj = Mahalla.objects.filter(name=mahalla_name).first()
            
            # Modelga ma'lumotlarni yozamiz
            app = Application.objects.create(
                telegram_id = update.effective_user.id,
                citizen_name=full_name,
                citizen_phone=phone_number,
                mahalla=mahalla_obj,
                age_medium=age_medium,
                content=text_content,
                status=Application.Status.NEW,
                priority=Application.Priority.LOW,
            )
            return app.app_number

        try:
            # Arizani bazaga saqlaymiz va avtomatik yaratilgan raqamini olamiz
            app_number = await save_application()
            
            await update.message.reply_text(
                f"✅ Arizangiz muvaffaqiyatli qabul qilindi!\n"
                f"🗂 Ariza raqami: {app_number}",
                reply_markup=ReplyKeyboardRemove()
            )
        except Exception as e:
            await update.message.reply_text(
                "❌ Arizani saqlashda texnik xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.",
                reply_markup=ReplyKeyboardRemove()
            )
            print(f"Ariza saqlashda xato: {e}")
            
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