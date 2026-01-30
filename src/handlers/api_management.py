from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from src.config import ALLOWED_USER_ID
from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from .base import auth_check, get_api_menu, get_nav_buttons, chunk_buttons, delete_user_message

INPUT_NAME, INPUT_URL, INPUT_KEY, INPUT_PASS = range(4)

TITLE_ADD_API = "*Add New API*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
TITLE_API_MGMT = "*API Management*\n━━━━━━━━━━━━━━━━━━━━━\n\n"


def escape_md(text: str) -> str:
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars:
        text = text.replace(char, f'\\{char}')
    return text


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("Cancel", callback_data="api_cancel")]])


async def api_add_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return ConversationHandler.END

    context.user_data["bot_msg"] = query.message

    text = TITLE_ADD_API + "Enter a name for this API:\n`example: main-server`"
    await query.edit_message_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN)
    return INPUT_NAME


async def input_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    name = update.message.text.strip().lower()
    bot_msg = context.user_data.get("bot_msg")

    if not name or len(name) < 2:
        text = TITLE_ADD_API + "Name must be at least 2 characters\\.\nTry again:"
        await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)
        return INPUT_NAME

    if not name.replace("-", "").replace("_", "").isalnum():
        text = TITLE_ADD_API + "Name can only contain letters, numbers, hyphens and underscores\\.\nTry again:"
        await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)
        return INPUT_NAME

    if await db.api_exists(name):
        text = TITLE_ADD_API + f"API `{name}` already exists\\.\nChoose another name:"
        await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)
        return INPUT_NAME

    context.user_data["api_name"] = name
    text = TITLE_ADD_API + f"*Name:* `{name}`\n\nEnter the API URL:\n`https://panel.example.com:4085/index.php`"
    await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN)
    return INPUT_URL


async def input_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    url = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")

    if not url.startswith(("http://", "https://")):
        text = TITLE_ADD_API + f"*Name:* `{name}`\n\nURL must start with `http://` or `https://`\nTry again:"
        await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN)
        return INPUT_URL

    context.user_data["api_url"] = url
    escaped_url = escape_md(url)
    text = TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\nEnter the API Key:"
    await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)
    return INPUT_KEY


async def input_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await delete_user_message(update)

    api_key = update.message.text.strip()
    bot_msg = context.user_data.get("bot_msg")
    name = context.user_data.get("api_name")
    url = context.user_data.get("api_url")

    if len(api_key) < 10:
        escaped_url = escape_md(url)
        text = TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\nAPI Key seems too short\\.\nTry again:"
        await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)
        return INPUT_KEY

    context.user_data["api_key"] = api_key
    escaped_url = escape_md(url)
    text = TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n*Key:* `{api_key[:8]}\\.\\.\\.`\n\nEnter the API Password:"
    await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)
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
        text = TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\nPassword seems too short\\.\nTry again:"
        await bot_msg.edit_text(text, reply_markup=get_cancel_keyboard(), parse_mode=ParseMode.MARKDOWN_V2)
        return INPUT_PASS

    text = TITLE_ADD_API + f"*Name:* `{name}`\n*URL:* `{escaped_url}`\n\n_Validating credentials\\.\\.\\._"
    await bot_msg.edit_text(text, parse_mode=ParseMode.MARKDOWN_V2)

    keyboard = [get_nav_buttons("menu_api", True)]

    try:
        api = VirtualizorAPI(url, key, api_pass)
        result = api.test_connection()
        await db.add_api(name, url, key, api_pass)

        text = f"*API Added Successfully*\n━━━━━━━━━━━━━━━━━━━━━\n\n*Name:* `{name}`\n*URL:* `{escaped_url}`\n*VMs Found:* `{result['vm_count']}`"
        await bot_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)

    except APIConnectionError as e:
        err = escape_md(str(e))
        text = f"*Connection Failed*\n━━━━━━━━━━━━━━━━━━━━━\n\n*Error:* `{err}`\n\n*Check:*\n\\- URL is correct\n\\- Server is online\n\\- Port is open"
        await bot_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)

    except AuthenticationError:
        text = "*Authentication Failed*\n━━━━━━━━━━━━━━━━━━━━━\n\nInvalid API Key or Password\\.\n\nVerify credentials in Virtualizor panel\\."
        await bot_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)

    except APIError as e:
        err = escape_md(str(e))
        text = f"*API Error*\n━━━━━━━━━━━━━━━━━━━━━\n\n*Error:* `{err}`"
        await bot_msg.edit_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)

    context.user_data.clear()
    return ConversationHandler.END


async def api_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.clear()

    text = TITLE_API_MGMT + "Select an option:"
    await query.edit_message_text(text, reply_markup=get_api_menu(), parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END


async def api_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()
    keyboard = [get_nav_buttons("menu_api", True)]

    if not apis:
        text = "*Saved APIs*\n━━━━━━━━━━━━━━━━━━━━━\n\n_No API configurations found\\._"
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)
        return

    text = "*Saved APIs*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for api in apis:
        default = " _\\[default\\]_" if api["is_default"] else ""
        escaped_url = escape_md(api['api_url'])
        text += f"*{api['name']}*{default}\n`{escaped_url}`\n\n"

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)


async def api_delete_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = "*Delete API*\n━━━━━━━━━━━━━━━━━━━━━\n\n_No APIs to delete\\._"
        keyboard = [get_nav_buttons("menu_api", True)]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)
        return

    text = "*Delete API*\n━━━━━━━━━━━━━━━━━━━━━\n\nSelect API to delete:"
    buttons = [InlineKeyboardButton(api["name"], callback_data=f"apidel_{api['name']}") for api in apis]
    keyboard = chunk_buttons(buttons, 2)
    keyboard.append(get_nav_buttons("menu_api", True))

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def api_delete_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    name = query.data.replace("apidel_", "")
    msg = f"API `{name}` deleted\\." if await db.delete_api(name) else f"API `{name}` not found\\."

    text = f"*Delete API*\n━━━━━━━━━━━━━━━━━━━━━\n\n{msg}"
    keyboard = [get_nav_buttons("menu_api", True)]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)


async def api_default_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = "*Set Default*\n━━━━━━━━━━━━━━━━━━━━━\n\n_No APIs configured\\._"
        keyboard = [get_nav_buttons("menu_api", True)]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)
        return

    text = "*Set Default*\n━━━━━━━━━━━━━━━━━━━━━\n\nSelect default API:"
    buttons = []
    for api in apis:
        label = f"{api['name']} *" if api["is_default"] else api["name"]
        buttons.append(InlineKeyboardButton(label, callback_data=f"apidef_{api['name']}"))
    keyboard = chunk_buttons(buttons, 2)
    keyboard.append(get_nav_buttons("menu_api", True))

    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN)


async def api_default_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not auth_check(query.from_user.id):
        return

    name = query.data.replace("apidef_", "")
    msg = f"`{name}` set as default\\." if await db.set_default(name) else f"API `{name}` not found\\."

    text = f"*Set Default*\n━━━━━━━━━━━━━━━━━━━━━\n\n{msg}"
    keyboard = [get_nav_buttons("menu_api", True)]
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN_V2)
