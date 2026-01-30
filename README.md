# Virtualizor Telegram Bot

A self-hosted Telegram bot for managing Virtualizor VMs via API. Designed for single-user operation with a clean, professional interface.

## Features

- Full button-based navigation (no commands needed except /start)
- Clean chat interface with auto-delete user messages
- Interactive menus using inline keyboards
- Markdown formatted messages
- Multiple API profile support with SQLite storage
- VM listing with status indicators
- Connection validation with detailed error messages
- Colored console logging with startup banner

## Requirements

- Python 3.10+
- Telegram Bot Token (from @BotFather)
- Virtualizor panel with API access enabled

## Project Structure

```
virtualizor-telegram-bot/
├── main.py
├── src/
│   ├── bot.py
│   ├── config.py
│   ├── logger.py
│   ├── api/
│   │   ├── client.py
│   │   └── exceptions.py
│   ├── database/
│   │   └── manager.py
│   └── handlers/
│       ├── base.py
│       ├── api_management.py
│       └── vm_management.py
├── data/
├── requirements.txt
└── .env
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd virtualizor-telegram-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
```

5. Edit `.env` with your credentials:
```
BOT_TOKEN=your-telegram-bot-token
ALLOWED_USER_ID=your-telegram-user-id
```

6. Run the bot:
```bash
python main.py
```

## Configuration

| Variable | Description |
|----------|-------------|
| BOT_TOKEN | Telegram bot token from @BotFather |
| ALLOWED_USER_ID | Your Telegram user ID |
| DATABASE_PATH | SQLite database path (default: data/bot.db) |

## Usage

1. Start the bot with `/start`
2. Navigate using inline buttons
3. All interactions are button-based for clean experience

Menu structure:
- Main Menu
  - API Management
    - Add API
    - List APIs
    - Set Default
    - Delete API
  - Virtual Machines
    - List VMs
    - VM Details (status, IP, VPS ID)

## Getting Credentials

- BOT_TOKEN: Message @BotFather on Telegram, send /newbot
- ALLOWED_USER_ID: Message @userinfobot on Telegram

## API Configuration

When adding an API, you need:
1. API URL (e.g., https://panel.example.com:4085/index.php)
2. API Key (from Virtualizor Admin Panel > Configuration > API Credentials)
3. API Password (from the same location)

## Console Output

The bot displays colored logs with a startup banner:
```
    ╔═══════════════════════════════════════════╗
    ║     Virtualizor Telegram Bot v1.0.0       ║
    ║     ─────────────────────────────────     ║
    ║     VM Management via Telegram            ║
    ╚═══════════════════════════════════════════╝

22:30:15    INFO bot          Starting bot...
22:30:15    INFO bot          Configuration loaded
22:30:15    INFO bot          Authorized user: 123456789
22:30:16    INFO bot          Database initialized
22:30:16    INFO bot          Bot is ready and listening for updates
```

## Security

- Single user access only
- API passwords stored encoded
- User messages auto-deleted
- SSL verification disabled for self-signed certificates

## Planned Features

- VM power controls (start/stop/restart)
- Port forwarding management
- Resource monitoring

## License

MIT
