"""API management handlers."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from src.config import ALLOWED_USER_ID
from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from .base import auth_check, get_api_menu, get_back_button, delete_user_message


# Conversation states
INPUT_NAME, INPUT_URL, INPUT_KEY, INPUT_PASS = range(4)


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
        text = text.replace(char, f"\\{char}")
    return text


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel button keyboard."""
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("Cancel", callback_data="api_cancel")]]
    )


async def api_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add API flow."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return ConversationHandler.END

    context.user_data["bot_msg"] = query.message

    text = (
        "*Add New API*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Enter a name for this API:\n"
        "`example: main-server`"
    )
    await query.edit_message_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN
    )
    return INPUT_NAME


async def input_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle name input."""
    await delete_user_message(update)

    name = update.message.text.strip().lower()
    bot_msg = context.user_data.get("bot_msg")

    if not name or len(name) < 2:
        text = (
            "*Add New API*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Name must be at least 2 characters\\.\n"
            "Try again:"
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_NAME

    if not name.replace("-", "").replace("_", "").isalnum():
        text = (
            "*Add New API*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Name can only contain letters, numbers, hyphens and underscores\\.\n"
            "Try again:"
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_NAME

    if await db.api_exists(name):
        text = (
            "*Add New API*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"API `{name}` already exists\\.\n"
            "Choose another name:"
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_NAME

    context.user_data["api_name"] = name
    text = (
        "*Add New API*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Name:* `{name}`\n\n"
        "Enter the API URL:\n"
        "`https://panel.example.com:4085/index.php`"
    )
    await bot_msg.edit_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN
    )
    return INPUT_URL


async def input_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle URL input."""
    await delete_user_message(update)

    url = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")

    if not url.startswith(("http://", "https://")):
        text = (
            "*Add New API*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Name:* `{name}`\n\n"
            "URL must start with `http://` or `https://`\n"
            "Try again:"
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN
        )
        return INPUT_URL

    context.user_data["api_url"] = url
    escaped_url = escape_md(url)
    text = (
        "*Add New API*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Name:* `{name}`\n"
        f"*URL:* `{escaped_url}`\n\n"
        "Enter the API Key:"
    )
    await bot_msg.edit_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
    )
    return INPUT_KEY


async def input_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle API key input."""
    await delete_user_message(update)

    api_key = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")
    url = context.user_data.get("api_url")

    if len(api_key) < 10:
        escaped_url = escape_md(url)
        text = (
            "*Add New API*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Name:* `{name}`\n"
            f"*URL:* `{escaped_url}`\n\n"
            "API Key seems too short\\.\n"
            "Try again:"
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_KEY

    context.user_data["api_key"] = api_key
    escaped_url = escape_md(url)
    text = (
        "*Add New API*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Name:* `{name}`\n"
        f"*URL:* `{escaped_url}`\n"
        f"*Key:* `{api_key[:8]}\\.\\.\\.`\n\n"
        "Enter the API Password:"
    )
    await bot_msg.edit_text(
        text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
    )
    return INPUT_PASS


async def input_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle password input and validate."""
    await delete_user_message(update)

    api_pass = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")
    url = context.user_data.get("api_url")
    key = context.user_data.get("api_key")

    escaped_url = escape_md(url)

    if len(api_pass) < 5:
        text = (
            "*Add New API*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Name:* `{name}`\n"
            f"*URL:* `{escaped_url}`\n\n"
            "Password seems too short\\.\n"
            "Try again:"
        )
        await bot_msg.edit_text(
            text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2
        )
        return INPUT_PASS

    # Show validating status
    text = (
        "*Add New API*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"*Name:* `{name}`\n"
        f"*URL:* `{escaped_url}`\n\n"
        "_Validating credentials\\.\\.\\._"
    )
    await bot_msg.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)

    try:
        api = VirtualizorAPI(url, key, api_pass)
        result = api.test_connection()
        await db.add_api(name, url, key, api_pass)

        text = (
            "*API Added Successfully*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Name:* `{name}`\n"
            f"*URL:* `{escaped_url}`\n"
            f"*VMs Found:* `{result['vm_count']}`"
        )
        await bot_msg.edit_text(
            text,
            reply_markup=get_back_button("menu_api"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIConnectionError as e:
        err = escape_md(str(e))
        text = (
            "*Connection Failed*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"*Error:* `{err}`\n\n"
            "*Check:*\n"
            "\\- URL is correct\n"
            "\\- Server is online\n"
            "\\- Port is open"
        )
        await bot_msg.edit_text(
            text,
            reply_markup=get_back_button("menu_api"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except AuthenticationError:
        text = (
            "*Authentication Failed*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Invalid API Key or Password\\.\n\n"
            "Verify credentials in Virtualizor panel\\."
        )
        await bot_msg.edit_text(
            text,
            reply_markup=get_back_button("menu_api"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    except APIError as e:
        err = escape_md(str(e))
        text = "*API Error*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"*Error:* `{err}`"
        await bot_msg.edit_text(
            text,
            reply_markup=get_back_button("menu_api"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    context.user_data.clear()
    return ConversationHandler.END


async def api_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel API operation."""
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    text = "*API Management*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "Select an option:"
    await query.edit_message_text(
        text, reply_markup=get_api_menu(), parse_mode=ParseMode.MARKDOWN
    )
    return ConversationHandler.END


async def api_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all APIs."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = (
            "*Saved APIs*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_No API configurations found\\._"
        )
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("menu_api"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    text = "*Saved APIs*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for api in apis:
        default = " _\\[default\\]_" if api["is_default"] else ""
        escaped_url = escape_md(api["api_url"])
        text += f"*{api['name']}*{default}\n`{escaped_url}`\n\n"

    await query.edit_message_text(
        text, reply_markup=get_back_button("menu_api"), parse_mode=ParseMode.MARKDOWN_V2
    )


async def api_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start delete API flow."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = "*Delete API*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "_No APIs to delete\\._"
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("menu_api"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    keyboard = []
    for api in apis:
        keyboard.append(
            [InlineKeyboardButton(api["name"], callback_data=f"apidel_{api['name']}")]
        )
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="menu_api")])

    text = "*Delete API*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "Select API to delete:"
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN
    )


async def api_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Confirm and delete API."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    name = query.data.replace("apidel_", "")

    if await db.delete_api(name):
        msg = f"API `{name}` deleted\\."
    else:
        msg = f"API `{name}` not found\\."

    text = "*Delete API*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"{msg}"
    await query.edit_message_text(
        text, reply_markup=get_back_button("menu_api"), parse_mode=ParseMode.MARKDOWN_V2
    )


async def api_default_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start set default flow."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = "*Set Default*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "_No APIs configured\\._"
        await query.edit_message_text(
            text,
            reply_markup=get_back_button("menu_api"),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    keyboard = []
    for api in apis:
        label = f"{api['name']} [current]" if api["is_default"] else api["name"]
        keyboard.append(
            [InlineKeyboardButton(label, callback_data=f"apidef_{api['name']}")]
        )
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="menu_api")])

    text = "*Set Default*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" "Select default API:"
    await query.edit_message_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN
    )


async def api_default_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set API as default."""
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    name = query.data.replace("apidef_", "")

    if await db.set_default(name):
        msg = f"`{name}` set as default\\."
    else:
        msg = f"API `{name}` not found\\."

    text = "*Set Default*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"{msg}"
    await query.edit_message_text(
        text, reply_markup=get_back_button("menu_api"), parse_mode=ParseMode.MARKDOWN_V2
    )
