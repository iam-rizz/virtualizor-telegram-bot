# Virtualizor Telegram Bot

<div align="center">

[![Quality Gate Status](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=alert_status&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Lines of Code](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=ncloc&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Maintainability Rating](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=software_quality_maintainability_rating&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Security Rating](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=software_quality_security_rating&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)

</div>

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
- **Batch Add APIs** - Add multiple connections at once
- User-friendly API names with spaces and case preservation
- VM listing with specs (vCPU, RAM, Storage, OS)
- VM status indicators (Running, Stopped, Suspended)
- Detailed VM info with real-time resource usage:
  - IPv4 and IPv6 addresses
  - RAM, Disk, Bandwidth usage with progress bars
  - Port forwarding rules count
  - OS and virtualization type
- Connection validation with detailed error messages
- Colored console logging with startup banner
- Auto-update notification with one-click update

## Requirements

- Python 3.10+
- Telegram Bot Token (from @BotFather)
- Virtualizor panel with API access enabled
- Ubuntu/Debian (tested on Ubuntu 22.04, Debian 12/13)

## What's New in v2.2

- **Batch Add APIs** - Add multiple API connections at once
- Bulk import support with simple format: `name|url|key|password`
- Comprehensive validation and testing for each API
- Detailed results showing success/failure status
- User-friendly API names with case preservation and spaces

## Previous Updates

### v2.1
- API names now preserve original case (e.g., "Main Server")
- Support for spaces in API names
- Case-insensitive uniqueness check

### v2.0
- Migrated from python-telegram-bot to aiogram 3.24.0
- Modern async-first architecture with Router system
- Built-in FSM (Finite State Machine) for cleaner conversation flows
- Improved performance and memory efficiency
- Cleaner, more pythonic code structure

## Project Structure

```
virtualizor-telegram-bot/
├── main.py
├── start.sh              # Auto-setup and start script
├── update.sh             # Update and restart script
├── src/
│   ├── bot.py
│   ├── config.py
│   ├── logger.py
│   ├── version.py
│   ├── updater.py
│   ├── api/
│   │   ├── client.py
│   │   └── exceptions.py
│   ├── database/
│   │   └── manager.py
│   └── routers/          # aiogram routers (was handlers/)
│       ├── base.py
│       ├── api_management.py
│       └── vm_management.py
├── data/
├── requirements.txt
└── .env
```

## Quick Start (Recommended)

```bash
git clone https://github.com/iam-rizz/virtualizor-telegram-bot.git
cd virtualizor-telegram-bot
chmod +x start.sh update.sh
./start.sh
```

The script will:
1. Check and install Python dependencies (python3, python3-venv, pip)
2. Create virtual environment and install requirements
3. Create `.env` from template (edit with your credentials)
4. Start bot with PM2 (if available) or screen

## Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/iam-rizz/virtualizor-telegram-bot.git
cd virtualizor-telegram-bot
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file:
```bash
cp .env.example .env
nano .env
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

## Update Bot

### Via Telegram
When a new version is available, an "Update Bot" button will appear in the main menu. Click it to automatically update and restart.

### Via Command Line
```bash
./update.sh
```

## Configuration

| Variable | Description |
|----------|-------------|
| BOT_TOKEN | Telegram bot token from @BotFather |
| ALLOWED_USER_IDS | Comma-separated Telegram user IDs (e.g., 123456789,987654321) |
| DATABASE_PATH | SQLite database path (default: data/bot.db) |

## Process Management

### With PM2 (Recommended)
```bash
# View logs
pm2 logs virtualizor-bot

# Restart
pm2 restart virtualizor-bot

# Stop
pm2 stop virtualizor-bot
```

### With Screen
```bash
# Attach to session
screen -r virtualizor-bot

# Detach
Ctrl+A then D

# Stop
screen -S virtualizor-bot -X quit
```

## Usage

1. Start the bot with `/start`
2. Navigate using inline buttons
3. All interactions are button-based for clean experience

Menu structure:
- Main Menu
  - API Management
    - Add API (single)
    - Batch Add (multiple at once)
    - List APIs
    - Set Default
    - Delete API
  - Virtual Machines
    - Select API (if multiple)
    - List VMs
    - VM Details (status, IP, VPS ID, resources)
  - About
  - Update Bot (when available)

## Getting Credentials

- BOT_TOKEN: Message @BotFather on Telegram, send /newbot
- ALLOWED_USER_ID: Message @userinfobot on Telegram

## API Configuration

### Single API
When adding an API, you need:
1. API URL (e.g., https://panel.example.com:4085/index.php)
2. API Key (from Virtualizor Admin Panel > Configuration > API Credentials)
3. API Password (from the same location)

### Batch Add APIs
Add multiple APIs at once using this format (one per line):
```
Main Server|https://panel1.com:4085/index.php|key123|pass123
NAT Panel|https://panel2.com:4085/index.php|key456|pass456
Backup VPS|https://panel3.com:4085/index.php|key789|pass789
```

**Format Rules:**
- Use `|` as separator
- One API per line
- All fields required (name, URL, key, password)
- Maximum 10 APIs per batch
- Each API is validated and tested before saving

## Tested On

- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS
- Debian 12
- Debian 13

## Security

- Single user access only
- API passwords stored encoded
- User messages auto-deleted
- HTTPS required for API connections

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
