# Release v2.0 - Migrate to aiogram 3.24.0

## 🚨 Breaking Change

This is a **major version release** that migrates from `python-telegram-bot` to `aiogram 3.24.0`. While all features remain the same, the underlying library has changed completely.

## ✨ What's New

### Modern Architecture
- **Async-first design** - Built on aiogram's modern async architecture
- **Router system** - Modular code organization with separate routers
- **Built-in FSM** - Cleaner conversation flows without ConversationHandler
- **Magic filters** - Intuitive filtering with `F.data`, `F.text`, etc.

### Performance Improvements
- ⚡ Faster update processing
- 💾 Lower memory footprint
- 🔄 Better async handling
- 📊 Improved efficiency

### Code Quality
- 🎯 Cleaner, more pythonic syntax
- 📦 Better modular structure
- 🧪 Easier to test and maintain
- 📝 Improved type hints

## 📋 Changes

### Library Migration
```diff
- python-telegram-bot==22.6
+ aiogram==3.24.0
```

### Structure Changes
```
src/handlers/  →  src/routers/
```

### New Files
- `MIGRATION_v1.0.7.md` - Comprehensive migration guide
- `CHANGELOG.md` - Full version history
- `src/routers/` - New router-based handlers

### Removed Files
- `src/handlers/` - Old handler structure

## 🔄 Migration

### For New Users
Just follow the normal installation:
```bash
git clone https://github.com/iam-rizz/virtualizor-telegram-bot.git
cd virtualizor-telegram-bot
chmod +x start.sh update.sh
./start.sh
```

### For Existing Users (v1.0.6 → v2.0)

**Option 1: Using update script (Recommended)**
```bash
./update.sh
```

**Option 2: Manual update**
```bash
git pull origin main
source venv/bin/activate
pip uninstall -y python-telegram-bot
pip install -r requirements.txt

# Restart bot
pm2 restart virtualizor-bot
# or
screen -S virtualizor-bot -X quit
./start.sh
```

See [MIGRATION_v2.0.md](MIGRATION_v2.0.md) for detailed migration guide.

## ✅ Compatibility

### Unchanged
- ✓ All features work exactly the same
- ✓ Database schema unchanged
- ✓ Configuration (.env) unchanged
- ✓ User experience identical
- ✓ API endpoints unchanged

### Requirements
- Python 3.10+
- Ubuntu/Debian (tested on Ubuntu 22.04, Debian 12/13)
- Telegram Bot Token
- Virtualizor panel with API access

## 📚 Documentation

- [MIGRATION_v2.0.md](MIGRATION_v2.0.md) - Migration guide
- [CHANGELOG.md](CHANGELOG.md) - Full changelog
- [README.md](README.md) - Updated documentation

## 🎯 Why aiogram?

### Before (python-telegram-bot)
```python
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Done")
```

### After (aiogram)
```python
@router.callback_query(F.data == "button")
async def handler(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text("Done")
```

**Benefits:**
- Cleaner syntax
- Less boilerplate
- Better performance
- Modern Python patterns
- Active development

## 🐛 Known Issues

None reported. If you encounter issues:
1. Check logs: `pm2 logs virtualizor-bot`
2. Verify Python version: `python3 --version`
3. Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## 🔙 Rollback

If you need to rollback to v1.0.6:
```bash
git checkout v1.0.6
pip uninstall -y aiogram
pip install python-telegram-bot==22.6
pm2 restart virtualizor-bot
```

## 👥 Contributors

- [@iam-rizz](https://github.com/iam-rizz)

## 📞 Support

- **GitHub Issues:** [Report bugs](https://github.com/iam-rizz/virtualizor-telegram-bot/issues)
- **Telegram:** [@rizzid03](https://t.me/rizzid03)
- **Forum:** [IPv6Indonesia](https://t.me/IPv6Indonesia)

## 🙏 Acknowledgments

Thanks to the aiogram team for creating an excellent modern Telegram bot framework!

---

**Full Changelog:** [v1.0.6...v2.0](https://github.com/iam-rizz/virtualizor-telegram-bot/compare/v1.0.6...v2.0)
