# Migration Guide: v1.0.6 → v2.0

## Overview

Version 2.0 introduces a major refactor from `python-telegram-bot` to `aiogram 3.24.0`, bringing modern async-first architecture and improved performance.

## Breaking Changes

### Library Change
- **Old:** `python-telegram-bot==22.6`
- **New:** `aiogram==3.24.0`

### Architecture Changes

#### 1. Handlers → Routers
```
src/handlers/  →  src/routers/
```

The old `handlers` folder has been replaced with `routers` using aiogram's Router system.

#### 2. Import Changes
```python
# Old (python-telegram-bot)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

# New (aiogram)
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
```

#### 3. Handler Decorators
```python
# Old
@callback_handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

# New
@router.callback_query(F.data == "button")
async def button_click(callback: CallbackQuery):
    await callback.answer()
```

#### 4. Keyboard Building
```python
# Old
keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("Text", callback_data="data")]
])

# New
builder = InlineKeyboardBuilder()
builder.button(text="Text", callback_data="data")
keyboard = builder.as_markup()
```

#### 5. FSM (State Management)
```python
# Old (ConversationHandler)
INPUT_NAME, INPUT_URL = range(2)

api_conv = ConversationHandler(
    entry_points=[...],
    states={INPUT_NAME: [...]},
    fallbacks=[...]
)

# New (aiogram FSM)
class APIForm(StatesGroup):
    name = State()
    url = State()

@router.callback_query(F.data == "api_add")
async def start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(APIForm.name)

@router.message(APIForm.name)
async def input_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(APIForm.url)
```

## Benefits

### Performance
- Faster update processing
- Lower memory footprint
- Better async handling

### Code Quality
- Cleaner, more pythonic syntax
- Built-in FSM without ConversationHandler complexity
- Magic filters (F.data, F.text, etc.)
- Better type hints support

### Developer Experience
- Modular router system
- Easier to test and maintain
- Better error handling
- More intuitive API

## Migration Steps

If you're running v1.0.6 and want to update to v2.0:

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Update dependencies:**
   ```bash
   ./update.sh
   ```
   
   Or manually:
   ```bash
   source venv/bin/activate
   pip uninstall -y python-telegram-bot
   pip install -r requirements.txt
   ```

3. **Restart bot:**
   ```bash
   # If using PM2
   pm2 restart virtualizor-bot
   
   # If using screen
   screen -S virtualizor-bot -X quit
   ./start.sh
   ```

## Compatibility

- All existing features remain unchanged
- Database schema unchanged
- Configuration (.env) unchanged
- API endpoints unchanged
- User experience identical

## Technical Details

### Bot Initialization
```python
# Old
application = Application.builder().token(BOT_TOKEN).build()
application.run_polling()

# New
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN_V2))
dp = Dispatcher()
dp.include_router(base_router)
await dp.start_polling(bot)
```

### Router System
Each module now has its own router:
- `base_router` - Main menu, about, update
- `api_router` - API management with FSM
- `vm_router` - VM listing and details

### Magic Filters
```python
# Callback data matching
@router.callback_query(F.data == "exact_match")
@router.callback_query(F.data.startswith("prefix_"))

# Message filters
@router.message(Command("start"))
@router.message(F.text)
```

## Support

If you encounter issues after migration:
- Check logs: `pm2 logs virtualizor-bot` or `screen -r virtualizor-bot`
- Verify Python version: `python3 --version` (requires 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Rollback

To rollback to v1.0.6:
```bash
git checkout v1.0.6
pip uninstall -y aiogram
pip install python-telegram-bot==22.6
pm2 restart virtualizor-bot
```

---

**Version:** 2.0  
**Date:** February 2026  
**Author:** Rizz
