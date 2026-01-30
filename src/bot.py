"""Main bot module."""

import logging

from telegram.ext import Application, CommandHandler

from src.config import BOT_TOKEN, ALLOWED_USER_ID
from src.database import db
from src.handlers import (
    start,
    help_command,
    listapi,
    deleteapi_start,
    setdefault_start,
    get_addapi_handler,
    get_callback_handler,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Initialize database after bot starts."""
    await db.init()
    logger.info("Database initialized")


def create_application() -> Application:
    """Create and configure bot application."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set")

    if ALLOWED_USER_ID == 0:
        raise ValueError("ALLOWED_USER_ID not set")

    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(get_addapi_handler())
    application.add_handler(CommandHandler("listapi", listapi))
    application.add_handler(CommandHandler("deleteapi", deleteapi_start))
    application.add_handler(CommandHandler("setdefault", setdefault_start))
    application.add_handler(get_callback_handler())

    return application


def run():
    """Run the bot."""
    try:
        application = create_application()
        logger.info("Bot starting...")
        application.run_polling(allowed_updates=["message", "callback_query"])
    except ValueError as e:
        logger.error(str(e))
