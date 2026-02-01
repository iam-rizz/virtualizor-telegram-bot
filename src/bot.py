import asyncio
import traceback

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from src.config import BOT_TOKEN, ALLOWED_USER_IDS
from src.database import db
from src.logger import setup_logger, print_banner
from src.routers import base_router, api_router, vm_router

logger = setup_logger()


async def on_startup():
    await db.init()
    logger.info("Database initialized")
    logger.info("Bot is ready and listening for updates")


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set")

    if not ALLOWED_USER_IDS:
        raise ValueError("ALLOWED_USER_IDS not set")

    bot = Bot(
        token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2)
    )

    dp = Dispatcher()

    dp.include_router(base_router)
    dp.include_router(api_router)
    dp.include_router(vm_router)

    dp.startup.register(on_startup)

    logger.info("Configuration loaded")
    logger.info(f"Authorized users: {ALLOWED_USER_IDS}")

    try:
        await dp.start_polling(bot, allowed_updates=["message", "callback_query"])
    except Exception as e:
        logger.error(f"Error during polling: {e}")
        logger.error(traceback.format_exc())
    finally:
        await bot.session.close()


def run():
    print_banner()
    logger.info("Starting bot...")

    try:
        asyncio.run(main())
    except ValueError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
