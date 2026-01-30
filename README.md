# Virtualizor Telegram Bot

A self-hosted Telegram bot for managing Virtualizor VMs via API. Designed for single-user operation with a clean, professional interface.

## Features

- Add and validate Virtualizor API configurations
- Store multiple API profiles with SQLite
- Connection testing with detailed error messages
- Secure credential handling

## Requirements

- Python 3.10+
- Telegram Bot Token (from @BotFather)
- Virtualizor panel with API access enabled

## Project Structure

```
virtualizor-telegram-bot/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── bot.py              # Bot application setup
│   ├── config.py           # Configuration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py       # Virtualizor API client
│   │   └── exceptions.py   # API exceptions
│   ├── database/
│   │   ├── __init__.py
│   │   └── manager.py      # SQLite database handler
│   └── handlers/
│       ├── __init__.py
│       ├── base.py         # Base handlers (start, help)
│       └── api_management.py  # API CRUD handlers
├── data/                   # Database storage (auto-created)
├── requirements.txt
└── README.md
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
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
export BOT_TOKEN="your-telegram-bot-token"
export ALLOWED_USER_ID="your-telegram-user-id"
```

To get your Telegram user ID, message @userinfobot on Telegram.

5. Run the bot:
```bash
python main.py
```

## Configuration

| Variable | Description |
|----------|-------------|
| BOT_TOKEN | Telegram bot token from @BotFather |
| ALLOWED_USER_ID | Your Telegram user ID (only this user can access the bot) |
| DATABASE_PATH | SQLite database path (default: data/bot.db) |

## Commands

| Command | Description |
|---------|-------------|
| /start | Show welcome message and available commands |
| /addapi | Add new Virtualizor API configuration |
| /listapi | List all saved API configurations |
| /deleteapi | Remove an API configuration |
| /setdefault | Set default API for operations |
| /help | Show help message |

## API Configuration

When adding an API, you need:

1. API URL - Your Virtualizor panel URL (e.g., https://panel.example.com:4085/index.php)
2. API Key - Found in Virtualizor Admin Panel > Configuration > API Credentials
3. API Password - The API password from the same location

The bot validates credentials before saving by testing the connection to your Virtualizor panel.

## Security Notes

- Only the configured ALLOWED_USER_ID can interact with the bot
- API passwords are stored encoded in the local SQLite database
- Password messages are automatically deleted after processing
- SSL verification is disabled by default for self-signed certificates

## Planned Features

- List and manage VMs
- Port forwarding management
- VM power controls (start/stop/restart)
- Resource monitoring

## License

MIT
