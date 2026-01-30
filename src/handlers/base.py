"""Base handlers."""

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.config import ALLOWED_USER_ID


def auth_required(func):
    """Decorator to check user authorization."""

    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        if user_id != ALLOWED_USER_ID:
            await update.message.reply_text("Access denied.")
            return ConversationHandler.END
        return await func(update, context)

    return wrapper


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("Access denied.")
        return

    text = (
        "Virtualizor VM Manager\n"
        "----------------------\n\n"
        "Commands:\n"
        "/addapi - Add new API configuration\n"
        "/listapi - List saved APIs\n"
        "/deleteapi - Remove API configuration\n"
        "/setdefault - Set default API\n"
        "/vms - List virtual machines\n"
        "/help - Show this message"
    )
    await update.message.reply_text(text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    await start(update, context)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel conversation."""
    context.user_data.clear()
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END
