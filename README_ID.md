# Virtualizor Telegram Bot

Bot Telegram self-hosted untuk mengelola VM Virtualizor melalui API. Dirancang untuk penggunaan single-user dengan antarmuka yang bersih dan profesional.

## Fitur

- Navigasi full button (tidak perlu command kecuali /start)
- Antarmuka chat bersih dengan auto-delete pesan user
- Menu interaktif menggunakan inline keyboard
- Pesan dengan format Markdown
- Support multiple profil API dengan penyimpanan SQLite
- Daftar VM dengan indikator status
- Validasi koneksi dengan pesan error detail
- Console logging berwarna dengan banner startup

## Persyaratan

- Python 3.10+
- Token Bot Telegram (dari @BotFather)
- Panel Virtualizor dengan akses API aktif

## Struktur Project

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

## Instalasi

1. Clone repository:
```bash
git clone <repository-url>
cd virtualizor-telegram-bot
```

2. Buat virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Buat file `.env`:
```bash
cp .env.example .env
```

5. Edit `.env` dengan kredensial Anda:
```
BOT_TOKEN=token-bot-telegram-anda
ALLOWED_USER_ID=id-telegram-anda
```

6. Jalankan bot:
```bash
python main.py
```

## Konfigurasi

| Variable | Deskripsi |
|----------|-----------|
| BOT_TOKEN | Token bot Telegram dari @BotFather |
| ALLOWED_USER_ID | ID Telegram Anda |
| DATABASE_PATH | Path database SQLite (default: data/bot.db) |

## Penggunaan

1. Mulai bot dengan `/start`
2. Navigasi menggunakan tombol inline
3. Semua interaksi berbasis tombol untuk pengalaman yang bersih

Struktur menu:
- Menu Utama
  - API Management
    - Add API
    - List APIs
    - Set Default
    - Delete API
  - Virtual Machines
    - List VMs
    - VM Details (status, IP, VPS ID)

## Mendapatkan Kredensial

- BOT_TOKEN: Kirim pesan ke @BotFather di Telegram, ketik /newbot
- ALLOWED_USER_ID: Kirim pesan ke @userinfobot di Telegram

## Konfigurasi API

Saat menambahkan API, Anda memerlukan:
1. API URL (contoh: https://panel.example.com:4085/index.php)
2. API Key (dari Virtualizor Admin Panel > Configuration > API Credentials)
3. API Password (dari lokasi yang sama)

## Output Console

Bot menampilkan log berwarna dengan banner startup:
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

## Keamanan

- Akses single user saja
- Password API disimpan ter-encode
- Pesan user otomatis dihapus
- Verifikasi SSL dinonaktifkan untuk sertifikat self-signed

## Fitur yang Direncanakan

- Kontrol power VM (start/stop/restart)
- Manajemen port forwarding
- Monitoring resource

## Lisensi

MIT
