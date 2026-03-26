from telegram import Update
from telegram.ext import Application,CommandHandler,CallbackQueryHandler, MessageHandler,filters,ConversationHandler
from decouple import config

from handlers import start_bot,murojat_bot,barcha_command_bot
from handlers.service.aplication_service import ASK_COMMENT, aplication_service, save_comment

def main():

    application = Application.builder().token(config("TOKEN")).build()

    application.add_handler(CommandHandler('start',start_bot))
    application.add_handler(CommandHandler('murojatlar',murojat_bot))
    application.add_handler(CommandHandler('barcha',barcha_command_bot))
    application.add_handler(CommandHandler('statistika',barcha_command_bot))
    application.add_handler(CommandHandler('yordam',barcha_command_bot))
    
    conv_handler = ConversationHandler( 
    entry_points=[
        CallbackQueryHandler(aplication_service, pattern="^murojat_")
    ],
    states={
        ASK_COMMENT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment)
        ],
    },
    fallbacks=[],
    )
    application.add_handler(conv_handler)
    application.add_handler(CallbackQueryHandler(aplication_service,pattern=r"^murojat_"))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()