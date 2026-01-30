# Virtualizor Telegram Bot

[![Quality Gate Status](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=alert_status&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Lines of Code](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=ncloc&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Maintainability Rating](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=software_quality_maintainability_rating&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Security Rating](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=software_quality_security_rating&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)

### Recommended VPS, NAT VPS (Virtualizor) & Hosting

<div align="center">

Need a VPS to test this script? **[HostData.id](https://hostdata.id)** provides a wide selection of reliable hosting options at affordable prices.

[![HostData.id](https://img.shields.io/badge/HostData.id-VPS%20Trusted-FF6B35?style=flat&logo=server&logoColor=white)](https://hostdata.id) 
[![NAT VPS](https://img.shields.io/badge/NAT%20VPS-Start%20from%2015K/Month-00C851?style=flat)](https://hostdata.id/nat-vps)
[![VPS Indonesia](https://img.shields.io/badge/VPS%20Indonesia-Start%20from%20200K/Month-007ACC?style=flat&logo=server)](https://hostdata.id/vps-indonesia)
[![Dedicated Server](https://img.shields.io/badge/Dedicated%20Server-Enterprise%20Ready-8B5CF6?style=flat&logo=server)](https://hostdata.id/dedicated-server)

</div>

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
│   ├── version.py
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
git clone https://github.com/iam-rizz/virtualizor-telegram-bot.git
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
ALLOWED_USER_IDS=123456789,987654321
```

6. Run the bot:
```bash
python main.py
```

## Configuration

| Variable | Description |
|----------|-------------|
| BOT_TOKEN | Telegram bot token from @BotFather |
| ALLOWED_USER_IDS | Comma-separated Telegram user IDs (e.g., 123456789,987654321) |
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
    - Select API (if multiple)
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
║   Virtualizor Telegram Bot v1.0.1         ║
║   ─────────────────────────────────────   ║
║   VM Management via Telegram              ║
║   github.com/iam-rizz                     ║
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

## Author

- GitHub: [@iam-rizz](https://github.com/iam-rizz)
- Telegram: [@rizzid03](https://t.me/rizzid03)
- Forum: [IPv6Indonesia](https://t.me/IPv6Indonesia)

## License

MIT
