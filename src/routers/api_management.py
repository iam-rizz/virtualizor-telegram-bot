from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database import db
from src.api import VirtualizorAPI, APIError, APIConnectionError, AuthenticationError
from src.routers.base import (
    auth_check,
    get_api_menu,
    get_nav_buttons,
    FOOTER,
)

router = Router()

TITLE_ADD_API = "*Add New API*\n━━━━━━━━━━━━━━━━━━━━━\n\n"
TITLE_API_MGMT = "*API Management*\n━━━━━━━━━━━━━━━━━━━━━\n\n"


async def delete_user_message(message):
    try:
        await message.delete()
    except Exception:
        pass


class APIForm(StatesGroup):
    name = State()
    url = State()
    key = State()
    password = State()


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


def get_cancel_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Cancel", callback_data="api_cancel"))
    return builder.as_markup()


@router.callback_query(F.data == "api_add")
async def api_add_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    await state.update_data(bot_msg_id=callback.message.message_id)

    text = (
        TITLE_ADD_API + "Step 1 of 4: API Name\n\n"
        "Enter a unique name to identify this API connection\\.\n"
        "You can use letters, numbers, spaces, hyphens or underscores\\.\n\n"
        "_Examples:_ `Main Server`, `NAT Panel 01`, `Backup\\-VPS`" + FOOTER
    )
    await callback.message.edit_text(text, reply_markup=get_cancel_keyboard())
    await state.set_state(APIForm.name)


@router.message(APIForm.name)
async def input_name(message: Message, state: FSMContext):
    await delete_user_message(message)

    name = message.text.strip()
    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id")

    if not name or len(name) < 2:
        text = (
            TITLE_ADD_API + "Name must be at least 2 characters\\.\n"
            "Please enter a valid name for your API connection\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=get_cancel_keyboard(),
        )
        return

    if len(name) > 50:
        text = (
            TITLE_ADD_API + "Name is too long \\(max 50 characters\\)\\.\n"
            "Please enter a shorter name\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=get_cancel_keyboard(),
        )
        return

    if not all(c.isalnum() or c in " -_" for c in name):
        text = (
            TITLE_ADD_API
            + "Name can only contain letters, numbers, spaces, hyphens and underscores\\.\n"
            "Please enter a valid name\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=get_cancel_keyboard(),
        )
        return

    if await db.api_exists_case_insensitive(name):
        text = (
            TITLE_ADD_API + f"API `{escape_md(name)}` already exists\\.\n"
            "Please choose a different name for this connection\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(api_name=name)
    escaped_name = escape_md(name)
    text = (
        TITLE_ADD_API + f"Step 2 of 4: API URL\n\n"
        f"*Name:* `{escaped_name}`\n\n"
        "Enter your Virtualizor panel URL\\.\n"
        "Include the full path with port number\\.\n\n"
        "_Example:_ `https://panel\\.example\\.com:4085/index\\.php`" + FOOTER
    )
    await message.bot.edit_message_text(
        text,
        chat_id=message.chat.id,
        message_id=bot_msg_id,
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(APIForm.url)


@router.message(APIForm.url)
async def input_url(message: Message, state: FSMContext):
    await delete_user_message(message)

    url = message.text.strip()
    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id")
    name = data.get("api_name")
    escaped_name = escape_md(name)

    if not url.startswith("https://"):
        text = (
            TITLE_ADD_API + f"*Name:* `{escaped_name}`\n\n"
            "URL must start with `https://` for security\\.\n"
            "Please enter a valid HTTPS URL\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(api_url=url)
    escaped_url = escape_md(url)
    text = (
        TITLE_ADD_API + f"Step 3 of 4: API Key\n\n"
        f"*Name:* `{escaped_name}`\n*URL:* `{escaped_url}`\n\n"
        "Enter your API Key from Virtualizor panel\\.\n"
        "Find it in: Configuration \\> API Credentials" + FOOTER
    )
    await message.bot.edit_message_text(
        text,
        chat_id=message.chat.id,
        message_id=bot_msg_id,
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(APIForm.key)


@router.message(APIForm.key)
async def input_key(message: Message, state: FSMContext):
    await delete_user_message(message)

    api_key = message.text.strip()
    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id")
    name = data.get("api_name")
    url = data.get("api_url")
    escaped_name = escape_md(name)
    escaped_url = escape_md(url)

    if len(api_key) < 10:
        text = (
            TITLE_ADD_API + f"*Name:* `{escaped_name}`\n*URL:* `{escaped_url}`\n\n"
            "API Key seems too short\\.\n"
            "Please enter a valid API Key from your Virtualizor panel\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=get_cancel_keyboard(),
        )
        return

    await state.update_data(api_key=api_key)
    text = (
        TITLE_ADD_API + f"Step 4 of 4: API Password\n\n"
        f"*Name:* `{escaped_name}`\n*URL:* `{escaped_url}`\n*Key:* `{api_key[:8]}\\.\\.\\.`\n\n"
        "Enter your API Password\\.\n"
        "This is the password associated with your API Key\\." + FOOTER
    )
    await message.bot.edit_message_text(
        text,
        chat_id=message.chat.id,
        message_id=bot_msg_id,
        reply_markup=get_cancel_keyboard(),
    )
    await state.set_state(APIForm.password)


@router.message(APIForm.password)
async def input_pass(message: Message, state: FSMContext):
    await delete_user_message(message)

    api_pass = message.text.strip()
    data = await state.get_data()
    bot_msg_id = data.get("bot_msg_id")
    name = data.get("api_name")
    url = data.get("api_url")
    key = data.get("api_key")

    escaped_name = escape_md(name)
    escaped_url = escape_md(url)

    if len(api_pass) < 5:
        text = (
            TITLE_ADD_API + f"*Name:* `{escaped_name}`\n*URL:* `{escaped_url}`\n\n"
            "Password seems too short\\.\n"
            "Please enter a valid API Password\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=get_cancel_keyboard(),
        )
        return

    text = (
        TITLE_ADD_API + f"*Name:* `{escaped_name}`\n*URL:* `{escaped_url}`\n\n"
        "_Validating credentials\\.\\.\\._"
    )
    await message.bot.edit_message_text(
        text, chat_id=message.chat.id, message_id=bot_msg_id
    )

    builder = InlineKeyboardBuilder()
    for btn in get_nav_buttons("menu_api", True):
        builder.add(btn)
    builder.adjust(2)

    try:
        api = VirtualizorAPI(url, key, api_pass)
        result = api.test_connection()
        await db.add_api(name, url, key, api_pass)

        text = (
            f"*API Added Successfully*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your API connection has been saved\\.\n\n"
            f"*Name:* `{escaped_name}`\n"
            f"*URL:* `{escaped_url}`\n"
            f"*VMs Found:* `{result['vm_count']}`\n\n"
            "You can now view your VMs from the main menu\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=builder.as_markup(),
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
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=builder.as_markup(),
        )

    except AuthenticationError:
        text = (
            "*Authentication Failed*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Invalid API Key or Password\\.\n\n"
            "Please verify your credentials in the Virtualizor panel "
            "under Configuration \\> API Credentials\\." + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=builder.as_markup(),
        )

    except APIError as e:
        err = escape_md(str(e))
        text = (
            f"*API Error*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "An error occurred while communicating with the API\\.\n\n"
            f"*Error:* `{err}`" + FOOTER
        )
        await message.bot.edit_message_text(
            text,
            chat_id=message.chat.id,
            message_id=bot_msg_id,
            reply_markup=builder.as_markup(),
        )

    await state.clear()


@router.callback_query(F.data == "api_cancel")
async def api_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()

    text = (
        TITLE_API_MGMT + "Operation cancelled\\.\n\n"
        "Select an option to manage your API connections\\." + FOOTER
    )
    await callback.message.edit_text(text, reply_markup=get_api_menu())


@router.callback_query(F.data == "api_list")
async def api_list(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    apis = await db.list_apis()

    builder = InlineKeyboardBuilder()
    for btn in get_nav_buttons("menu_api", True):
        builder.add(btn)
    builder.adjust(2)

    if not apis:
        text = (
            "*Saved APIs*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_No API configurations found\\._\n\n"
            "You haven't added any API connections yet\\.\n"
            "Go back and select Add API to register your first Virtualizor panel\\."
            + FOOTER
        )
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        return

    text = (
        "*Saved APIs*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Your configured Virtualizor API connections\\.\n"
        "The default API is used when viewing VMs with single API\\.\n\n"
    )
    for api in apis:
        default = " _\\[default\\]_" if api["is_default"] else ""
        escaped_name = escape_md(api["name"])
        escaped_url = escape_md(api["api_url"])
        text += f"*{escaped_name}*{default}\n`{escaped_url}`\n\n"

    text += FOOTER

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "api_delete")
async def api_delete_start(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
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
        builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons("menu_api", True):
            builder.add(btn)
        builder.adjust(2)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        return

    text = (
        "*Delete API*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Select an API connection to permanently remove\\.\n"
        "This will delete all saved credentials for that connection\\.\n\n"
        "_This action cannot be undone\\._" + FOOTER
    )

    builder = InlineKeyboardBuilder()
    for api in apis:
        builder.button(text=api["name"], callback_data=f"apidel_{api['name']}")
    builder.adjust(2)

    nav_builder = InlineKeyboardBuilder()
    for btn in get_nav_buttons("menu_api", True):
        nav_builder.add(btn)
    nav_builder.adjust(2)

    builder.attach(nav_builder)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("apidel_"))
async def api_delete_confirm(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    name = callback.data.replace("apidel_", "")
    escaped_name = escape_md(name)
    success = await db.delete_api(name)

    if success:
        msg = f"API `{escaped_name}` has been deleted successfully\\."
    else:
        msg = f"API `{escaped_name}` was not found\\."

    text = f"*Delete API*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"{msg}" + FOOTER

    builder = InlineKeyboardBuilder()
    for btn in get_nav_buttons("menu_api", True):
        builder.add(btn)
    builder.adjust(2)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data == "api_default")
async def api_default_start(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    apis = await db.list_apis()

    if not apis:
        text = (
            "*Set Default*\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "_No APIs configured\\._\n\n"
            "You need to add an API connection first\\." + FOOTER
        )
        builder = InlineKeyboardBuilder()
        for btn in get_nav_buttons("menu_api", True):
            builder.add(btn)
        builder.adjust(2)
        await callback.message.edit_text(text, reply_markup=builder.as_markup())
        return

    text = (
        "*Set Default*\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose which API to use as your default connection\\.\n"
        "The default API is automatically selected when you have only one API\\.\n\n"
        "_\\* indicates current default_" + FOOTER
    )

    builder = InlineKeyboardBuilder()
    for api in apis:
        label = f"{api['name']} *" if api["is_default"] else api["name"]
        builder.button(text=label, callback_data=f"apidef_{api['name']}")
    builder.adjust(2)

    nav_builder = InlineKeyboardBuilder()
    for btn in get_nav_buttons("menu_api", True):
        nav_builder.add(btn)
    nav_builder.adjust(2)

    builder.attach(nav_builder)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(F.data.startswith("apidef_"))
async def api_default_confirm(callback: CallbackQuery):
    await callback.answer()

    if not auth_check(callback.from_user.id):
        return

    name = callback.data.replace("apidef_", "")
    escaped_name = escape_md(name)
    success = await db.set_default(name)

    if success:
        msg = f"`{escaped_name}` is now your default API connection\\."
    else:
        msg = f"API `{escaped_name}` was not found\\."

    text = f"*Set Default*\n" "━━━━━━━━━━━━━━━━━━━━━\n\n" f"{msg}" + FOOTER

    builder = InlineKeyboardBuilder()
    for btn in get_nav_buttons("menu_api", True):
        builder.add(btn)
    builder.adjust(2)

    await callback.message.edit_text(text, reply_markup=builder.as_markup())
