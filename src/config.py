import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")

_allowed_users = os.getenv("ALLOWED_USER_IDS", os.getenv("ALLOWED_USER_ID", ""))
ALLOWED_USER_IDS = [int(uid.strip()) for uid in _allowed_users.split(",") if uid.strip().isdigit()]

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/bot.db")
