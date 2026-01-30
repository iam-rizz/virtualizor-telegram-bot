"""Bot configuration."""

import os

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Allowed User ID (single user bot)
ALLOWED_USER_ID = int(os.getenv("ALLOWED_USER_ID", "0"))

# Database path
DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")
