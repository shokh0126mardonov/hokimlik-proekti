from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from handlers.utils import StepAplications
from decouple import config

# Barcha kerakli handlerlarni import qilish
from handlers import (
    start_bot,
    murojat_bot,
    help_command_bot,
    statistic_command_bot,
    get_full_name,
    get_average_age,
    get_mahalla,
    get_text,
    confirm_application,
    cancel,
    ariza_yuborish
)

from handlers.service.aplication_service import (
    ASK_COMMENT,
    ASK_FILE,
    save_comment,
    handle_file_upload,
    handle_status_actions,
)

from handlers.service import (
    get_contact,
    skip_file_callback,
)


def main():
    application = Application.builder().token(config("TOKEN")).build()

    application.add_handler(CommandHandler("start", start_bot))
    application.add_handler(CommandHandler("murojatlar", murojat_bot))
    application.add_handler(CommandHandler("yordam", help_command_bot))
    application.add_handler(CommandHandler("statistika", statistic_command_bot))

    application_conversetion = ConversationHandler(
        entry_points=[
            MessageHandler(filters.CONTACT, get_contact),
            CommandHandler("ariza", ariza_yuborish) 
        ],
        states={
            StepAplications.FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_full_name)],
            StepAplications.MAHALLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mahalla)],
            StepAplications.AVEREGE_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_average_age)],
            StepAplications.TEXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)],
            StepAplications.CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_application)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True,
        per_message=False  # ✅ Bu False bo'lgani ma'qul, aks holda CallbackQuery'lar bilan xato berishi mumkin
    )
    
    conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                handle_status_actions, pattern=r"^murojat_(kordim|organdim)_"
            )
        ],
        states={
            ASK_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment)
            ],
            ASK_FILE: [
                MessageHandler(
                    filters.PHOTO | filters.Document.ALL,
                    handle_file_upload,
                ),
                CallbackQueryHandler(skip_file_callback, pattern="^skip_file$"),
            ],
        },
        fallbacks=[],
        per_chat=True,
        per_user=True,
        allow_reentry=True
    )

    # Handlerlarni botga qo'shamiz (Faqat keraklilari)
    application.add_handler(application_conversetion)
    application.add_handler(conversation)

    # Botni ishga tushirish
    print("Bot muvaffaqiyatli ishga tushdi...")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()