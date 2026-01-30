from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.config import ALLOWED_USER_ID
from src.version import __version__, __author__, __github__, __telegram__, __forum__

BTN_BACK = "< Back"
BTN_HOME = "Home"


def auth_check(user_id: int) -> bool:
    return user_id == ALLOWED_USER_ID


def chunk_buttons(buttons: list, cols: int = 2) -> list:
    return [buttons[i:i + cols] for i in range(0, len(buttons), cols)]


def get_nav_buttons(back: str = None, home: bool = True) -> list:
    buttons = []
    if back:
        buttons.append(InlineKeyboardButton(BTN_BACK, callback_data=back))
    if home:
        buttons.append(InlineKeyboardButton(BTN_HOME, callback_data="menu_main"))
    return buttons


def get_main_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("API Management", callback_data="menu_api"),
            InlineKeyboardButton("Virtual Machines", callback_data="menu_vms"),
        ],
        [InlineKeyboardButton("About", callback_data="menu_about")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_api_menu() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("Add API", callback_data="api_add"),
            InlineKeyboardButton("List APIs", callback_data="api_list"),
        ],
        [
            InlineKeyboardButton("Set Default", callback_data="api_default"),
            InlineKeyboardButton("Delete API", callback_data="api_delete"),
        ],
        [InlineKeyboardButton(BTN_BACK, callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button(callback: str = "menu_main", home: bool = True) -> InlineKeyboardMarkup:
    buttons = get_nav_buttons(callback, home)
    return InlineKeyboardMarkup([buttons])


async def delete_user_message(update: Update):
    try:
        if update.message:
            await update.message.delete()
    except Exception:
        pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not auth_check(update.effective_user.id):
        await update.message.reply_text("Access denied.")
        return

    await delete_user_message(update)

    text = (
        "*Virtualizor VM Manager*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an option below:\n\n"
        "─────────────────────\n"
        f"`v{__version__}` \\| by {__author__}"
    )

    msg = await update.effective_chat.send_message(
        text, reply_markup=get_main_menu(), parse_mode=ParseMode.MARKDOWN_V2
    )
    context.user_data["main_msg_id"] = msg.message_id


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = (
        "*Virtualizor VM Manager*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an option below:\n\n"
        "─────────────────────\n"
        f"`v{__version__}` \\| by {__author__}"
    )
    await query.edit_message_text(
        text, reply_markup=get_main_menu(), parse_mode=ParseMode.MARKDOWN_V2
    )


async def show_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = "*API Management*\n━━━━━━━━━━━━━━━━━━━━━\n\nSelect an option:"
    await query.edit_message_text(
        text, reply_markup=get_api_menu(), parse_mode=ParseMode.MARKDOWN
    )


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = (
        "*About*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "*Virtualizor Telegram Bot*\n"
        f"Version: `{__version__}`\n\n"
        f"*Developer:* {__author__}\n"
        f"*GitHub:* [Repository]({__github__})\n"
        f"*Telegram:* [@rizzid03]({__telegram__})\n"
        f"*Forum:* [IPv6Indonesia]({__forum__})\n\n"
        "─────────────────────\n"
        "_A self\\-hosted bot for managing_\n"
        "_Virtualizor VMs via Telegram\\._"
    )

    keyboard = [
        [
            InlineKeyboardButton("GitHub", url=__github__),
            InlineKeyboardButton("Telegram", url=__telegram__),
        ],
        [InlineKeyboardButton("Forum", url=__forum__)],
        [InlineKeyboardButton(BTN_BACK, callback_data="menu_main")],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True
    )
