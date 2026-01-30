"""API management handlers."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from src.config import ALLOWED_USER_ID
from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from .base import auth_required, cancel


# Conversation states
API_NAME, API_URL, API_KEY, API_PASS = range(4)


@auth_required
async def addapi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add API conversation."""
    await update.message.reply_text(
        "Add New API Configuration\n"
        "-------------------------\n\n"
        "Enter a name for this API (e.g., main-server):\n\n"
        "Send /cancel to abort."
    )
    return API_NAME


async def addapi_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle API name input."""
    name = update.message.text.strip().lower()

    if not name or len(name) < 2:
        await update.message.reply_text(
            "Name must be at least 2 characters. Try again:"
        )
        return API_NAME

    if not name.replace("-", "").replace("_", "").isalnum():
        await update.message.reply_text(
            "Name can only contain letters, numbers, hyphens and underscores. Try again:"
        )
        return API_NAME

    if await db.api_exists(name):
        await update.message.reply_text(
            f"API '{name}' already exists. Choose another name:"
        )
        return API_NAME

    context.user_data["api_name"] = name
    await update.message.reply_text(
        f"Name: {name}\n\n"
        "Enter the API URL:\n"
        "(e.g., https://panel.example.com:4085/index.php)"
    )
    return API_URL


async def addapi_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle API URL input."""
    url = update.message.text.strip()

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text(
            "URL must start with http:// or https://. Try again:"
        )
        return API_URL

    context.user_data["api_url"] = url
    await update.message.reply_text("Enter the API Key:")
    return API_KEY


async def addapi_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle API key input."""
    api_key = update.message.text.strip()

    if len(api_key) < 10:
        await update.message.reply_text("API Key seems too short. Try again:")
        return API_KEY

    context.user_data["api_key"] = api_key
    await update.message.reply_text("Enter the API Password:")
    return API_PASS


async def addapi_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle API password input and validate."""
    api_pass = update.message.text.strip()

    # Delete the message containing password for security
    try:
        await update.message.delete()
    except Exception:
        pass

    if len(api_pass) < 5:
        await update.effective_chat.send_message(
            "API Password seems too short. Try again:"
        )
        return API_PASS

    name = context.user_data["api_name"]
    url = context.user_data["api_url"]
    key = context.user_data["api_key"]

    # Test connection
    status_msg = await update.effective_chat.send_message(
        "Validating API credentials..."
    )

    try:
        api = VirtualizorAPI(url, key, api_pass)
        result = api.test_connection()

        # Save to database
        await db.add_api(name, url, key, api_pass)

        await status_msg.edit_text(
            "API Added Successfully\n"
            "----------------------\n\n"
            f"Name: {name}\n"
            f"URL: {url}\n"
            f"VMs Found: {result['vm_count']}"
        )
    except APIConnectionError as e:
        await status_msg.edit_text(
            "Connection Failed\n"
            "-----------------\n\n"
            f"Error: {e}\n\n"
            "Please check:\n"
            "- URL is correct and accessible\n"
            "- Server is online\n"
            "- Port is open\n\n"
            "Use /addapi to try again."
        )
    except AuthenticationError:
        await status_msg.edit_text(
            "Authentication Failed\n"
            "---------------------\n\n"
            "Invalid API Key or Password.\n\n"
            "Please verify your credentials in Virtualizor panel.\n\n"
            "Use /addapi to try again."
        )
    except APIError as e:
        await status_msg.edit_text(
            "API Error\n" "---------\n\n" f"Error: {e}\n\n" "Use /addapi to try again."
        )
    finally:
        context.user_data.clear()

    return ConversationHandler.END


@auth_required
async def listapi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all saved APIs."""
    apis = await db.list_apis()

    if not apis:
        await update.message.reply_text(
            "No API configurations found.\n\n" "Use /addapi to add one."
        )
        return

    text = "Saved API Configurations\n------------------------\n\n"
    for api in apis:
        default = " [default]" if api["is_default"] else ""
        text += f"- {api['name']}{default}\n  {api['api_url']}\n\n"

    await update.message.reply_text(text)


@auth_required
async def deleteapi_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start delete API flow."""
    apis = await db.list_apis()

    if not apis:
        await update.message.reply_text("No API configurations to delete.")
        return

    keyboard = []
    for api in apis:
        keyboard.append(
            [InlineKeyboardButton(api["name"], callback_data=f"del_{api['name']}")]
        )
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="del_cancel")])

    await update.message.reply_text(
        "Select API to delete:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def deleteapi_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle delete API callback."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ALLOWED_USER_ID:
        return

    data = query.data
    if data == "del_cancel":
        await query.edit_message_text("Cancelled.")
        return

    name = data.replace("del_", "")
    if await db.delete_api(name):
        await query.edit_message_text(f"API '{name}' deleted.")
    else:
        await query.edit_message_text(f"API '{name}' not found.")


@auth_required
async def setdefault_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start set default API flow."""
    apis = await db.list_apis()

    if not apis:
        await update.message.reply_text("No API configurations found.")
        return

    keyboard = []
    for api in apis:
        label = f"{api['name']} [current]" if api["is_default"] else api["name"]
        keyboard.append(
            [InlineKeyboardButton(label, callback_data=f"def_{api['name']}")]
        )
    keyboard.append([InlineKeyboardButton("Cancel", callback_data="def_cancel")])

    await update.message.reply_text(
        "Select default API:", reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def setdefault_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle set default callback."""
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ALLOWED_USER_ID:
        return

    data = query.data
    if data == "def_cancel":
        await query.edit_message_text("Cancelled.")
        return

    name = data.replace("def_", "")
    if await db.set_default(name):
        await query.edit_message_text(f"'{name}' set as default API.")
    else:
        await query.edit_message_text(f"API '{name}' not found.")


def get_addapi_handler() -> ConversationHandler:
    """Get add API conversation handler."""
    return ConversationHandler(
        entry_points=[CommandHandler("addapi", addapi_start)],
        states={
            API_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, addapi_name)],
            API_URL: [MessageHandler(filters.TEXT & ~filters.COMMAND, addapi_url)],
            API_KEY: [MessageHandler(filters.TEXT & ~filters.COMMAND, addapi_key)],
            API_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, addapi_pass)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


def get_callback_handler() -> CallbackQueryHandler:
    """Get callback query handler."""

    async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
        data = update.callback_query.data
        if data.startswith("del_"):
            await deleteapi_callback(update, context)
        elif data.startswith("def_"):
            await setdefault_callback(update, context)

    return CallbackQueryHandler(callback_router)
