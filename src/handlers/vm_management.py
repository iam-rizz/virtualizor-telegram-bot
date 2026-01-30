"""VM management handlers."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from .base import auth_check, get_back_button


def escape_md(text: str) -> str:
    """Escape markdown special characters."""
    chars = [
        "_",
        "*",
        "[",
        "]",
        "(",
        ")",
        "~",
        "`",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in chars:
        text = str(text).replace(char, f"\\{char}")
    return text


def get_vm_menu() -> InlineKeyboardMarkup:
    """Get VM menu keyboard."""
    keyboard = [
        [InlineKeyboardButton("List VMs", callback_data="vm_list")],
        [InlineKeyboardButton("< Back", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def show_vms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show VMs menu."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    # Check if API is configured
    api_config = await db.get_default_api()
    if not api_config:
        text = (
            "*Virtual Machines*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_No API configured\\._\n\n"
            "Add an API first in API Management\\."
        )
        await query.edit_message_text(
            text, reply_markup=get_back_button(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return

    text = (
        "*Virtual Machines*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Active API:* `{api_config['name']}`\n\n"
        "Select an option:"
    )
    await query.edit_message_text(
        text, reply_markup=get_vm_menu(), parse_mode=ParseMode.MARKDOWN
    )


async def vm_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all VMs."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    api_config = await db.get_default_api()
    if not api_config:
        text = (
            "*Virtual Machines*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "_No API configured\\._"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("menu_vms"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    # Show loading
    text = "*Virtual Machines*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "_Loading VMs\\.\\.\\._"
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2)

    try:
        api = VirtualizorAPI.from_db_config(api_config)
        vms = api.list_vms()

        if not vms:
            text = (
                "*Virtual Machines*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "_No VMs found\\._"
            )
            await query.edit_message_text(
                text,
                reply_markup=get_back_button("menu_vms"),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return

        # Build VM list with buttons
        text = f"*Virtual Machines* \\({len(vms)}\\)\n━━━━━━━━━━━━━━━━━━━━━\n\n"

        keyboard = []
        for vm in vms:
            status_icon = "●" if vm["status"] == "running" else "○"
            hostname = escape_md(vm["hostname"])
            ip = escape_md(vm["ipv4"] or "No IP")

            text += f"{status_icon} *{hostname}*\n"
            text += f"    `{ip}`\n\n"

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{status_icon} {vm['hostname'][:20]}",
                        callback_data=f"vm_{vm['vpsid']}",
                    )
                ]
            )

        keyboard.append([InlineKeyboardButton("Refresh", callback_data="vm_list")])
        keyboard.append([InlineKeyboardButton("< Back", callback_data="menu_vms")])

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIConnectionError as e:
        err = escape_md(str(e))
        text = "*Connection Error*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"`{err}`"
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("menu_vms"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except AuthenticationError:
        text = (
            "*Authentication Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_Invalid API credentials\\._"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("menu_vms"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIError as e:
        err = escape_md(str(e))
        text = "*API Error*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"`{err}`"
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("menu_vms"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def vm_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show VM details."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    vpsid = query.data.replace("vm_", "")

    api_config = await db.get_default_api()
    if not api_config:
        return

    # Show loading
    text = "*VM Details*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "_Loading\\.\\.\\._"
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2)

    try:
        api = VirtualizorAPI.from_db_config(api_config)
        vms = api.list_vms()

        vm = None
        for v in vms:
            if v["vpsid"] == vpsid:
                vm = v
                break

        if not vm:
            text = "*VM Details*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "_VM not found\\._"
            await query.edit_message_text(
                text,
                reply_markup=get_back_button("vm_list"),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return

        status_text = "Running" if vm["status"] == "running" else "Stopped"
        status_icon = "●" if vm["status"] == "running" else "○"
        hostname = escape_md(vm["hostname"])
        ip = escape_md(vm["ipv4"] or "No IP")

        text = (
            f"*{hostname}*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Status:* {status_icon} {status_text}\n"
            f"*IP:* `{ip}`\n"
            f"*VPS ID:* `{vpsid}`"
        )

        keyboard = [
            [InlineKeyboardButton("Refresh", callback_data=f"vm_{vpsid}")],
            [InlineKeyboardButton("< Back", callback_data="vm_list")],
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except (APIConnectionError, AuthenticationError, APIError) as e:
        err = escape_md(str(e))
        text = "*Error*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"`{err}`"
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("vm_list"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
