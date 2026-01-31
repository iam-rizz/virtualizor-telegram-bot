from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from .base import auth_check, get_nav_buttons, chunk_buttons, BTN_BACK, FOOTER

TITLE_VM = "*Virtual Machines*\n━━━━━━━━━━━━━━━━━━━━━\n\n"


def escape_md(text: str) -> str:
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


async def show_vms_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = (
            TITLE_VM + "_No API configured\\._\n\n"
            "You need to add an API connection first to view your virtual machines\\.\n"
            "Go to API Management to add your Virtualizor credentials\\." + FOOTER
        )
        keyboard = [[InlineKeyboardButton(BTN_BACK, callback_data="menu_main")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    if len(apis) == 1:
        context.user_data["selected_api"] = apis[0]["name"]
        await _show_vm_list(query, context, apis[0])
        return

    text = (
        TITLE_VM + "You have multiple API servers configured\\.\n"
        "Select which Virtualizor panel to view VMs from\\.\n\n"
        "_\\* indicates default API_" + FOOTER
    )
    buttons = []
    for api in apis:
        default = " *" if api["is_default"] else ""
        buttons.append(
            InlineKeyboardButton(
                f"{api['name']}{default}", callback_data=f"vmapi_{api['name']}"
            )
        )

    keyboard = chunk_buttons(buttons, 2)
    keyboard.append([InlineKeyboardButton(BTN_BACK, callback_data="menu_main")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def vm_select_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    api_name = query.data.replace("vmapi_", "")
    api_config = await db.get_api(api_name)

    if not api_config:
        text = (
            TITLE_VM + "_API not found\\._\n\n"
            "The selected API configuration could not be found\\." + FOOTER
        )
        keyboard = [get_nav_buttons("menu_vms", True)]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    context.user_data["selected_api"] = api_name
    await _show_vm_list(query, context, api_config)


async def _show_vm_list(query, context: ContextTypes.DEFAULT_TYPE, api_config: dict):
    api_name = api_config["name"]
    escaped_api_name = escape_md(api_name)

    text = TITLE_VM + f"*API:* `{escaped_api_name}`\n\n_Loading VMs\\.\\.\\._"
    await query.edit_message_text(text, parse_mode=ParseMode.MARKDOWN_V2)

    try:
        api = VirtualizorAPI.from_db_config(api_config)
        vms = api.list_vms()

        if not vms:
            text = (
                TITLE_VM + f"*API:* `{escaped_api_name}`\n\n"
                "_No VMs found\\._\n\n"
                "This Virtualizor panel has no virtual machines configured\\." + FOOTER
            )
            keyboard = [get_nav_buttons("menu_vms", True)]
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return

        text = (
            f"*Virtual Machines* \\({len(vms)}\\)\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*API:* `{escaped_api_name}`\n\n"
            "Showing all VMs from this Virtualizor panel\\.\n"
            "Select a VM to view details\\.\n\n"
            "● Running  ○ Stopped\n\n"
        )

        buttons = []
        for vm in vms:
            status_icon = "●" if vm["status"] == "running" else "○"
            hostname = escape_md(vm["hostname"])
            ip = escape_md(vm["ipv4"] or "No IP")

            text += f"{status_icon} *{hostname}*\n    `{ip}`\n\n"

            btn_name = (
                vm["hostname"][:15] + ".."
                if len(vm["hostname"]) > 15
                else vm["hostname"]
            )
            buttons.append(
                InlineKeyboardButton(
                    f"{status_icon} {btn_name}",
                    callback_data=f"vm_{api_config['name']}_{vm['vpsid']}",
                )
            )

        text += FOOTER

        keyboard = chunk_buttons(buttons, 2)
        keyboard.append(
            [
                InlineKeyboardButton(
                    "Refresh", callback_data=f"vmapi_{api_config['name']}"
                )
            ]
        )
        keyboard.append(get_nav_buttons("menu_vms", True))

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIConnectionError as e:
        text = (
            f"*Connection Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Unable to connect to the Virtualizor panel\\.\n\n"
            f"`{escape_md(str(e))}`" + FOOTER
        )
        keyboard = [get_nav_buttons("menu_vms", True)]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except AuthenticationError:
        text = (
            "*Authentication Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_Invalid API credentials\\._\n\n"
            "Please check your API Key and Password in API Management\\." + FOOTER
        )
        keyboard = [get_nav_buttons("menu_vms", True)]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIError as e:
        text = (
            f"*API Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "An error occurred while fetching VMs\\.\n\n"
            f"`{escape_md(str(e))}`" + FOOTER
        )
        keyboard = [get_nav_buttons("menu_vms", True)]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )


async def vm_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_vms_menu(update, context)


async def vm_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    parts = query.data.split("_", 2)
    if len(parts) < 3:
        return

    api_name = parts[1]
    vpsid = parts[2]
    escaped_api_name = escape_md(api_name)

    api_config = await db.get_api(api_name)
    if not api_config:
        return

    text = "*VM Details*\n━━━━━━━━━━━━━━━━━━━━━\n\n_Loading\\.\\.\\._"
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
            text = (
                "*VM Details*\n"
                "━━━━━━━━━━━━━━━━━━━━━\n\n"
                "_VM not found\\._\n\n"
                "The virtual machine could not be found\\. "
                "It may have been deleted or the VPS ID is invalid\\." + FOOTER
            )
            keyboard = [get_nav_buttons(f"vmapi_{api_name}", True)]
            await query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(keyboard),
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
            "Detailed information about this virtual machine\\.\n\n"
            f"*API:* `{escaped_api_name}`\n"
            f"*Status:* {status_icon} {status_text}\n"
            f"*IP Address:* `{ip}`\n"
            f"*VPS ID:* `{vpsid}`\n\n"
            "_Click Refresh to update the status\\._" + FOOTER
        )

        keyboard = [
            [InlineKeyboardButton("Refresh", callback_data=f"vm_{api_name}_{vpsid}")],
            get_nav_buttons(f"vmapi_{api_name}", True),
        ]

        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except (APIConnectionError, AuthenticationError, APIError) as e:
        text = (
            f"*Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "An error occurred while fetching VM details\\.\n\n"
            f"`{escape_md(str(e))}`" + FOOTER
        )
        keyboard = [get_nav_buttons(f"vmapi_{api_name}", True)]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
