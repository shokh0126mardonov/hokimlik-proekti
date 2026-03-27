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

from handlers import start_bot, murojat_bot, barcha_command_bot

from handlers.service.aplication_service import (
    ASK_COMMENT,
    ASK_FILE,
    save_comment,
    handle_file_upload,
    handle_comment_entry,
    handle_file_entry,
    handle_status_actions,
)


def main():
    application = Application.builder().token(config("TOKEN")).build()

    # =========================
    # COMMANDS
    # =========================
    application.add_handler(CommandHandler("start", start_bot))
    application.add_handler(CommandHandler("murojatlar", murojat_bot))
    application.add_handler(CommandHandler("barcha", barcha_command_bot))
    application.add_handler(CommandHandler("statistika", barcha_command_bot))
    application.add_handler(CommandHandler("yordam", barcha_command_bot))

    # =========================
    # COMMENT CONVERSATION
    # =========================
    comment_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_comment_entry, pattern=r"^murojat_comment_")
        ],
        states={
            ASK_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, save_comment)
            ],
        },
        fallbacks=[],
        per_chat=True,
        per_user=True,
    )

    # =========================
    # FILE CONVERSATION
    # =========================
    file_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handle_file_entry, pattern=r"^murojat_file_")
        ],
        states={
            ASK_FILE: [
                MessageHandler(
                    filters.PHOTO | filters.Document.ALL,
                    handle_file_upload,
                )
            ],
        },
        fallbacks=[],
        per_chat=True,
        per_user=True,
    )

    # =========================
    # HANDLER ORDER (CRITICAL)
    # =========================
    application.add_handler(comment_conv)
    application.add_handler(file_conv)

    # FAqat stateless actionlar
    application.add_handler(
        CallbackQueryHandler(
            handle_status_actions,
            pattern=r"^murojat_(kordim|organdim)_"
        )
    )

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()