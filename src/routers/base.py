from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from src.config import ALLOWED_USER_IDS
from src.version import __version__, __author__, __github__, __telegram__, __forum__
from src.updater import check_for_updates, run_update

router = Router()

BTN_BACK = "< Back"
BTN_HOME = "Home"
FOOTER = f"\n\n─────────────────────\n`v{__version__}` \\| by _[{__author__}](tg://user?id=7898378667)_"


def auth_check(user_id: int) -> bool:
    return user_id in ALLOWED_USER_IDS


def get_nav_buttons(back: str = None, home: bool = True) -> list:
    buttons = []
    if back:
        buttons.append(InlineKeyboardButton(text=BTN_BACK, callback_data=back))
    if home:
        buttons.append(InlineKeyboardButton(text=BTN_HOME, callback_data="menu_main"))
    return buttons


async def get_dynamic_footer() -> str:
    update_info = await check_for_updates()
    if update_info["update_available"]:
        return f"\n\n─────────────────────\n`v{__version__}` _\\(v{update_info['latest']} available\\)_"
    return f"\n\n─────────────────────\n`v{__version__}` \\| by _[{__author__}](tg://user?id=7898378667)_"


async def get_main_menu():
    update_info = await check_for_updates()
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="API Management", callback_data="menu_api"),
        InlineKeyboardButton(text="Virtual Machines", callback_data="menu_vms"),
    )
    builder.row(InlineKeyboardButton(text="About", callback_data="menu_about"))

    if update_info["update_available"]:
        builder.row(
            InlineKeyboardButton(
                text=f"Update Bot (v{update_info['latest']})",
                callback_data="bot_update",
            )
        )

    return builder.as_markup()


def get_api_menu():
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="Add API", callback_data="api_add"),
        InlineKeyboardButton(text="Batch Add", callback_data="api_batch_add"),
    )
    builder.row(
        InlineKeyboardButton(text="List APIs", callback_data="api_list"),
        InlineKeyboardButton(text="Set Default", callback_data="api_default"),
    )
    builder.row(InlineKeyboardButton(text="Delete API", callback_data="api_delete"))
    builder.row(InlineKeyboardButton(text=BTN_BACK, callback_data="menu_main"))

    return builder.as_markup()


async def delete_user_message(message: Message):
    try:
        await message.delete()
    except Exception:
        pass


@router.message(Command("start"))
async def start(message: Message):
    if not auth_check(message.from_user.id):
        await message.answer("Access denied.")
        return

    await delete_user_message(message)
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

    await message.answer(text, reply_markup=await get_main_menu())


@router.callback_query(F.data == "menu_main")
async def show_main_menu(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
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

    await callback.message.edit_text(text, reply_markup=await get_main_menu())


@router.callback_query(F.data == "menu_api")
async def show_api_menu(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
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

    await callback.message.edit_text(text, reply_markup=get_api_menu())


@router.callback_query(F.data == "menu_about")
async def show_about(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
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

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=BTN_BACK, callback_data="menu_main"))

    await callback.message.edit_text(
        text, reply_markup=builder.as_markup(), disable_web_page_preview=True
    )


@router.callback_query(F.data == "bot_update")
async def bot_update(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    text = (
        "*Update Bot*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "_Starting update process\\.\\.\\._\n\n"
        "The bot will pull the latest changes and restart\\.\n"
        "Please wait a moment\\."
    )

    await callback.message.edit_text(text)

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

    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text=BTN_HOME, callback_data="menu_main"))

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
