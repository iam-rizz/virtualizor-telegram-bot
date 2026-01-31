from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from .base import (
    auth_check,
    get_api_menu,
    get_nav_buttons,
    chunk_buttons,
    delete_user_message,
    FOOTER,
)

INPUT_NAME, INPUT_URL, INPUT_KEY, INPUT_PASS = range(4)

TITLE_ADD_API = "*Add New API*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
TITLE_API_MGMT = "*API Management*\n━━━━━━━━━━━━━━━━━━━━━\n\n"


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
        text = text.replace(char, f"\\{char}")
    return text


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Cancel", callback_data="api_cancel")]]
    )


async def api_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return ConversationHandler.END

    context.user_data["bot_msg"] = query.message

    text = (
        TITLE_ADD_API + "Step 1 of 4: API Name\n\n"
        "Enter a unique name to identify this API connection\\.\n"
        "Use lowercase letters, numbers, hyphens or underscores\\.\n\n"
        "_Example:_ `main\\-server`" + FOOTER
    )
    await query.edit_message_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
    )
    return INPUT_NAME


async def input_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    name = update.message.text.strip().lower()
    bot_msg = context.user_data.get("bot_msg")

    if not name or len(name) < 2:
        text = (
            TITLE_ADD_API + "Name must be at least 2 characters\\.\n"
            "Please enter a valid name for your API connection\\." + FOOTER
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_NAME

    if not name.replace("-", "").replace("_", "").isalnum():
        text = (
            TITLE_ADD_API
            + "Name can only contain letters, numbers, hyphens and underscores\\.\n"
            "Please enter a valid name\\." + FOOTER
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_NAME

    if await db.api_exists(name):
        text = (
            TITLE_ADD_API + f"API `{name}` already exists\\.\n"
            "Please choose a different name for this connection\\." + FOOTER
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_NAME

    context.user_data["api_name"] = name
    text = (
        TITLE_ADD_API + f"Step 2 of 4: API URL\n\n"
        f"*Name:* `{name}`\n\n"
        "Enter your Virtualizor panel URL\\.\n"
        "Include the full path with port number\\.\n\n"
        "_Example:_ `https://panel\\.example\\.com:4085/index\\.php`" + FOOTER
    )
    await bot_msg.edit_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
    )
    return INPUT_URL


async def input_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    url = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")

    if not url.startswith("https://"):
        text = (
            TITLE_ADD_API + f"*Name:* `{name}`\n\n"
            "URL must start with `https://` for security\\.\n"
            "Please enter a valid HTTPS URL\\." + FOOTER
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_URL

    context.user_data["api_url"] = url
    escaped_url = escape_md(url)
    text = (
        TITLE_ADD_API + f"Step 3 of 4: API Key\n\n"
        f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\n"
        "Enter your API Key from Virtualizor panel\\.\n"
        "Find it in: Configuration \\> API Credentials" + FOOTER
    )
    await bot_msg.edit_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
    )
    return INPUT_KEY


async def input_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    api_key = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")
    url = context.user_data.get("api_url")

    if len(api_key) < 10:
        escaped_url = escape_md(url)
        text = (
            TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\n"
            "API Key seems too short\\.\n"
            "Please enter a valid API Key from your Virtualizor panel\\." + FOOTER
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_KEY

    context.user_data["api_key"] = api_key
    escaped_url = escape_md(url)
    text = (
        TITLE_ADD_API + f"Step 4 of 4: API Password\n\n"
        f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n*Key:* `{api_key[:8]}\\.\\.\\.`\n\n"
        "Enter your API Password\\.\n"
        "This is the password associated with your API Key\\." + FOOTER
    )
    await bot_msg.edit_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
    )
    return INPUT_PASS


async def input_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    api_pass = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")
    url = context.user_data.get("api_url")
    key = context.user_data.get("api_key")

    escaped_url = escape_md(url)

    if len(api_pass) < 5:
        text = (
            TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\n"
            "Password seems too short\\.\n"
            "Please enter a valid API Password\\." + FOOTER
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_PASS

    text = (
        TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\n"
        "_Validating credentials\\.\\.\\._"
    )
    await bot_msg.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)

    keyboard = [get_nav_buttons("menu_api", True)]

    try:
        api = VirtualizorAPI(url, key, api_pass)
        result = api.test_connection()
        await db.add_api(name, url, key, api_pass)

        text = (
            f"*API Added Successfully*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your API connection has been saved\\.\n\n"
            f"*Name:* `{name}`\n"
            f"*URL:* `{escaped_url}`\n"
            f"*VMs Found:* `{result['vm_count']}`\n\n"
            "You can now view your VMs from the main menu\\." + FOOTER
        )
        await bot_msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIConnectionError as e:
        err = escape_md(str(e))
        text = (
            f"*Connection Failed*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Unable to connect to the Virtualizor panel\\.\n\n"
            f"*Error:* `{err}`\n\n"
            "*Please check:*\n"
            "\\- URL is correct\n"
            "\\- Server is online\n"
            "\\- Port is open" + FOOTER
        )
        await bot_msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except AuthenticationError:
        text = (
            "*Authentication Failed*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Invalid API Key or Password\\.\n\n"
            "Please verify your credentials in the Virtualizor panel "
            "under Configuration \\> API Credentials\\." + FOOTER
        )
        await bot_msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIError as e:
        err = escape_md(str(e))
        text = (
            f"*API Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "An error occurred while communicating with the API\\.\n\n"
            f"*Error:* `{err}`" + FOOTER
        )
        await bot_msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    context.user_data.clear()
    return ConversationHandler.END


async def api_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    text = (
        TITLE_API_MGMT + "Operation cancelled\\.\n\n"
        "Select an option to manage your API connections\\." + FOOTER
    )
    await query.edit_message_text(
        text, reply_markup=get_api_menu(), parse_mode=ParseMode.MARKDOWN_V2
    )
    return ConversationHandler.END


async def api_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()
    keyboard = [get_nav_buttons("menu_api", True)]

    if not apis:
        text = (
            "*Saved APIs*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_No API configurations found\\._\n\n"
            "You haven't added any API connections yet\\.\n"
            "Go back and select Add API to register your first Virtualizor panel\\."
            + FOOTER
        )
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    text = (
        "*Saved APIs*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Your configured Virtualizor API connections\\.\n"
        "The default API is used when viewing VMs with single API\\.\n\n"
    )
    for api in apis:
        default = " _\\[default\\]_" if api["is_default"] else ""
        escaped_url = escape_md(api["api_url"])
        text += f"*{api['name']}*{default}\n`{escaped_url}`\n\n"

    text += FOOTER

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def api_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = (
            "*Delete API*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_No APIs to delete\\._\n\n"
            "You need to add an API connection first before you can delete one\\."
            + FOOTER
        )
        keyboard = [get_nav_buttons("menu_api", True)]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    text = (
        "*Delete API*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an API connection to permanently remove\\.\n"
        "This will delete all saved credentials for that connection\\.\n\n"
        "_This action cannot be undone\\._" + FOOTER
    )
    buttons = [
        InlineKeyboardButton(api["name"], callback_data=f"apidel_{api['name']}")
        for api in apis
    ]
    keyboard = chunk_buttons(buttons, 2)
    keyboard.append(get_nav_buttons("menu_api", True))

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def api_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    name = query.data.replace("apidel_", "")
    success = await db.delete_api(name)

    if success:
        msg = f"API `{name}` has been deleted successfully\\."
    else:
        msg = f"API `{name}` was not found\\."

    text = f"*Delete API*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"{msg}" + FOOTER
    keyboard = [get_nav_buttons("menu_api", True)]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def api_default_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = (
            "*Set Default*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_No APIs configured\\._\n\n"
            "You need to add an API connection first\\." + FOOTER
        )
        keyboard = [get_nav_buttons("menu_api", True)]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    text = (
        "*Set Default*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose which API to use as your default connection\\.\n"
        "The default API is automatically selected when you have only one API\\.\n\n"
        "_\\* indicates current default_" + FOOTER
    )
    buttons = []
    for api in apis:
        label = f"{api['name']} *" if api["is_default"] else api["name"]
        buttons.append(
            InlineKeyboardButton(label, callback_data=f"apidef_{api['name']}")
        )
    keyboard = chunk_buttons(buttons, 2)
    keyboard.append(get_nav_buttons("menu_api", True))

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )


async def api_default_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    name = query.data.replace("apidef_", "")
    success = await db.set_default(name)

    if success:
        msg = f"`{name}` is now your default API connection\\."
    else:
        msg = f"API `{name}` was not found\\."

    text = f"*Set Default*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"{msg}" + FOOTER
    keyboard = [get_nav_buttons("menu_api", True)]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
