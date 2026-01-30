"""Bot configuration."""

import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")
