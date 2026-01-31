from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.config import ALLOWED_USER_IDS
from src.version import __version__, __author__, __github__, __telegram__, __forum__
from src.updater import check_for_updates, run_update

BTN_BACK = "< Back"
BTN_HOME = "Home"
FOOTER = f"\n\n─────────────────────\n`v{__version__}` \\| by _[{__author__}](tg://user?id=7898378667)_"


def auth_check(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS


def chunk_buttons(buttons: list, cols: int = 2) -> list:
    return [buttons[i : i + cols] for i in range(0, len(buttons), cols)]


def get_nav_buttons(back: str = None, home: bool = True) -> list:
    buttons = []
    if back:
        buttons.append(InlineKeyboardButton(BTN_BACK, callback_data=back))
    if home:
        buttons.append(InlineKeyboardButton(BTN_HOME, callback_data="menu_main"))
    return buttons


async def get_dynamic_footer() -> str:
    update_info = await check_for_updates()
    if update_info["update_available"]:
        return f"\n\n─────────────────────\n`v{__version__}` _\\(v{update_info['latest']} available\\)_"
    return f"\n\n─────────────────────\n`v{__version__}` \\| by _[{__author__}](tg://user?id=7898378667)_"


async def get_main_menu() -> InlineKeyboardMarkup:
    update_info = await check_for_updates()
    keyboard = [
        [
            InlineKeyboardButton("API Management", callback_data="menu_api"),
            InlineKeyboardButton("Virtual Machines", callback_data="menu_vms"),
        ],
        [InlineKeyboardButton("About", callback_data="menu_about")],
    ]
    if update_info["update_available"]:
        keyboard.append(
            [
                InlineKeyboardButton(
                    f"Update Bot (v{update_info['latest']})", callback_data="bot_update"
                )
            ]
        )
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


def get_back_button(
    callback: str = "menu_main", home: bool = True
) -> InlineKeyboardMarkup:
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
    footer = await get_dynamic_footer()

    text = (
        "*Virtualizor Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Welcome to Virtualizor Management Bot\\.\n\n"
        "This bot helps you manage your Virtualizor VPS servers "
        "directly from Telegram\\. You can add multiple API connections, "
        "view your virtual machines, and monitor their status\\.\n\n"
        "*Getting Started:*\n"
        "1\\. Add your Virtualizor API credentials\n"
        "2\\. View and manage your VMs\n\n"
        "Select an option below to continue\\." + footer
    )

    await update.message.reply_text(
        text, reply_markup=await get_main_menu(), parse_mode=ParseMode.MARKDOWN_V2
    )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    footer = await get_dynamic_footer()

    text = (
        "*Virtualizor Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Main Menu\n\n"
        "*API Management* \\- Configure your Virtualizor API connections\\. "
        "Add, remove, or set default API credentials\\.\n\n"
        "*Virtual Machines* \\- View and monitor all VMs from your "
        "connected Virtualizor panels\\.\n\n"
        "Select an option to continue\\." + footer
    )

    await query.edit_message_text(
        text, reply_markup=await get_main_menu(), parse_mode=ParseMode.MARKDOWN_V2
    )


async def show_api_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = (
        "*API Management*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Manage your Virtualizor API connections\\.\n\n"
        "*Add API* \\- Register a new Virtualizor panel connection\\.\n"
        "*List APIs* \\- View all saved API configurations\\.\n"
        "*Set Default* \\- Choose which API to use by default\\.\n"
        "*Delete API* \\- Remove an API connection\\.\n\n"
        "Select an option to continue\\." + FOOTER
    )

    await query.edit_message_text(
        text, reply_markup=get_api_menu(), parse_mode=ParseMode.MARKDOWN_V2
    )


async def show_about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = (
        "*About*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Version:* `{__version__}`\n"
        f"*Author:* {__author__}\n\n"
        "*Links:*\n"
        f"[GitHub Repository]({__github__})\n"
        f"[Telegram Contact]({__telegram__})\n"
        f"[Community Forum]({__forum__})\n\n"
        "A simple and elegant Telegram bot for managing "
        "Virtualizor VPS servers\\. Self\\-hosted and secure\\." + FOOTER
    )

    keyboard = [[InlineKeyboardButton(BTN_BACK, callback_data="menu_main")]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
        disable_web_page_preview=True,
    )


async def bot_update(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    text = (
        "*Update Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "_Starting update process\\.\\.\\._\n\n"
        "The bot will pull the latest changes and restart\\.\n"
        "Please wait a moment\\."
    )

    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2)

    result = run_update()

    if result["success"]:
        text = (
            "*Update Bot*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Update initiated\\.\n\n"
            "The bot will restart shortly\\.\n"
            "Use /start after restart\\."
        )
    else:
        text = (
            "*Update Bot*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"_Update failed:_ `{result['message']}`\n\n"
            "Please run `\\./update\\.sh` manually\\." + FOOTER
        )

    keyboard = [[InlineKeyboardButton(BTN_HOME, callback_data="menu_main")]]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
