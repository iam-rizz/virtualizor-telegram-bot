import warnings

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.config import BOT_TOKEN, ALLOWED_USER_ID
from src.database import db
from src.logger import setup_logger, print_banner
from src.handlers import (
    start,
    show_main_menu,
    show_api_menu,
    show_about,
    show_vms_menu,
    api_add_start,
    input_name,
    input_url,
    input_key,
    input_pass,
    api_cancel,
    api_list,
    api_delete_start,
    api_delete_confirm,
    api_default_start,
    api_default_confirm,
    vm_list,
    vm_detail,
    vm_select_api,
    INPUT_NAME,
    INPUT_URL,
    INPUT_KEY,
    INPUT_PASS,
)

logger = setup_logger()


async def post_init(application: Application):
    await db.init()
    logger.info("Database initialized")
    logger.info("Bot is ready and listening for updates")


def create_application() -> Application:
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set")

    if ALLOWED_USER_ID == 0:
        raise ValueError("ALLOWED_USER_ID not set")

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    api_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(api_add_start, pattern="^api_add$")],
        states={
            INPUT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_name)],
            INPUT_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_url)],
            INPUT_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_key)],
            INPUT_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_pass)],
        },
        fallbacks=[CallbackQueryHandler(api_cancel, pattern="^api_cancel$")],
        per_message=False,
        per_chat=True,
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(api_conv)

    application.add_handler(CallbackQueryHandler(show_main_menu, pattern="^menu_main$"))
    application.add_handler(CallbackQueryHandler(show_api_menu, pattern="^menu_api$"))
    application.add_handler(CallbackQueryHandler(show_vms_menu, pattern="^menu_vms$"))
    application.add_handler(CallbackQueryHandler(show_about, pattern="^menu_about$"))

    application.add_handler(CallbackQueryHandler(api_list, pattern="^api_list$"))
    application.add_handler(CallbackQueryHandler(api_delete_start, pattern="^api_delete$"))
    application.add_handler(CallbackQueryHandler(api_delete_confirm, pattern="^apidel_"))
    application.add_handler(CallbackQueryHandler(api_default_start, pattern="^api_default$"))
    application.add_handler(CallbackQueryHandler(api_default_confirm, pattern="^apidef_"))

    application.add_handler(CallbackQueryHandler(vm_select_api, pattern="^vmapi_"))
    application.add_handler(CallbackQueryHandler(vm_list, pattern="^vm_list$"))
    application.add_handler(CallbackQueryHandler(vm_detail, pattern="^vm_"))

    return application


def run():
    warnings.filterwarnings("ignore", message=".*per_message.*")

    print_banner()
    logger.info("Starting bot...")

    try:
        application = create_application()
        logger.info("Configuration loaded")
        logger.info(f"Authorized user: {ALLOWED_USER_ID}")
        application.run_polling(allowed_updates=["message", "callback_query"])
    except ValueError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
