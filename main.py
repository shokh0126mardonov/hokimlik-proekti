from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
)
from decouple import config

from handlers import (
    start_bot,
    murojat_bot,
    help_command_bot,
    statistic_command_bot,
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

    # =========================
    # COMMANDS
    # =========================
    application.add_handler(CommandHandler("start", start_bot))
    application.add_handler(CommandHandler("murojatlar", murojat_bot))
    application.add_handler(CommandHandler("yordam", help_command_bot))
    application.add_handler(CommandHandler("statistika", statistic_command_bot))
    application.add_handler(MessageHandler(filters.CONTACT,get_contact))

    # =========================
    # SINGLE CONVERSATION
    # =========================
    conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                handle_status_actions,
                pattern=r"^murojat_(kordim|organdim)_"
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
            CallbackQueryHandler(skip_file_callback, pattern="^skip_file$")
            ],
        },
        fallbacks=[],
        per_chat=True,
        per_user=True,
    )

    application.add_handler(conversation)

    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )

    


if __name__ == "__main__":
    main()