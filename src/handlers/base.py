"""Base handlers."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.config import ALLOWED_USER_ID


def auth_check(user_id: int) -> bool:
    """Check if user is authorized."""
    return user_id == ALLOWED_USER_ID


def get_main_menu() -> InlineKeyboardMarkup:
    """Get main menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("API Management", callback_data="menu_api")],
        [InlineKeyboardButton("Virtual Machines", callback_data="menu_vms")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_api_menu() -> InlineKeyboardMarkup:
    """Get API management menu."""
    keyboard = [
        [InlineKeyboardButton("Add API", callback_data="api_add")],
        [InlineKeyboardButton("List APIs", callback_data="api_list")],
        [InlineKeyboardButton("Set Default", callback_data="api_default")],
        [InlineKeyboardButton("Delete API", callback_data="api_delete")],
        [InlineKeyboardButton("< Back", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button(callback: str = "menu_main") -> InlineKeyboardMarkup:
    """Get back button."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("< Back", callback_data=callback)]]
    )


async def delete_user_message(update: Update):
    """Delete user message to keep chat clean."""
    try:
        if update.message:
            await update.message.delete()
    except Exception:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    if not auth_check(update.effective_user.id):
        await update.message.reply_text("Access denied.")
        return

    await delete_user_message(update)

    text = (
        "*Virtualizor VM Manager*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an option below:"
    )

    msg = await update.effective_chat.send_message(
        text, reply_markup=get_main_menu(), parse_mode=ParseMode.MARKDOWN
    )
    context.user_data["main_msg_id"] = msg.message_id


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu via callback."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = (
        "*Virtualizor VM Manager*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an option below:"
    )
    await query.edit_message_text(
        text, reply_markup=get_main_menu(), parse_mode=ParseMode.MARKDOWN
    )


async def show_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show API management menu."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = "*API Management*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "Select an option:"
    await query.edit_message_text(
        text, reply_markup=get_api_menu(), parse_mode=ParseMode.MARKDOWN
    )
