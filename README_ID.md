# Virtualizor Telegram Bot

Bot Telegram self-hosted untuk mengelola VM Virtualizor melalui API. Dirancang untuk penggunaan single-user dengan antarmuka yang bersih dan profesional.

## Fitur

- Tambah dan validasi konfigurasi API Virtualizor
- Simpan beberapa profil API dengan SQLite
- Pengujian koneksi dengan pesan error detail
- Penanganan kredensial yang aman

## Persyaratan

- Python 3.10+
- Token Bot Telegram (dari @BotFather)
- Panel Virtualizor dengan akses API aktif

## Struktur Project

```
virtualizor-telegram-bot/
├── main.py                 # Entry point
├── src/
│   ├── __init__.py
│   ├── bot.py              # Setup aplikasi bot
│   ├── config.py           # Konfigurasi
│   ├── api/
│   │   ├── __init__.py
│   │   ├── client.py       # Virtualizor API client
│   │   └── exceptions.py   # API exceptions
│   ├── database/
│   │   ├── __init__.py
│   │   └── manager.py      # SQLite database handler
│   └── handlers/
│       ├── __init__.py
│       ├── base.py         # Handler dasar (start, help)
│       └── api_management.py  # Handler CRUD API
├── data/                   # Penyimpanan database (auto-created)
├── requirements.txt
└── README.md
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
# atau
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Konfigurasi environment variables:
```bash
export BOT_TOKEN="token-bot-telegram-anda"
export ALLOWED_USER_ID="id-telegram-anda"
```

Untuk mendapatkan Telegram user ID, kirim pesan ke @userinfobot di Telegram.

5. Jalankan bot:
```bash
python main.py
```

## Konfigurasi

| Variable | Deskripsi |
|----------|-----------|
| BOT_TOKEN | Token bot Telegram dari @BotFather |
| ALLOWED_USER_ID | ID Telegram Anda (hanya user ini yang bisa akses bot) |
| DATABASE_PATH | Path database SQLite (default: data/bot.db) |

## Perintah

| Perintah | Deskripsi |
|----------|-----------|
| /start | Tampilkan pesan selamat datang dan perintah tersedia |
| /addapi | Tambah konfigurasi API Virtualizor baru |
| /listapi | Daftar semua konfigurasi API tersimpan |
| /deleteapi | Hapus konfigurasi API |
| /setdefault | Set API default untuk operasi |
| /help | Tampilkan pesan bantuan |

## Konfigurasi API

Saat menambahkan API, Anda memerlukan:

1. API URL - URL panel Virtualizor Anda (contoh: https://panel.example.com:4085/index.php)
2. API Key - Ditemukan di Virtualizor Admin Panel > Configuration > API Credentials
3. API Password - Password API dari lokasi yang sama

Bot memvalidasi kredensial sebelum menyimpan dengan menguji koneksi ke panel Virtualizor Anda.

## Catatan Keamanan

- Hanya ALLOWED_USER_ID yang dikonfigurasi yang dapat berinteraksi dengan bot
- Password API disimpan ter-encode di database SQLite lokal
- Pesan password otomatis dihapus setelah diproses
- Verifikasi SSL dinonaktifkan secara default untuk sertifikat self-signed

## Fitur yang Direncanakan

- Daftar dan kelola VM
- Manajemen port forwarding
- Kontrol power VM (start/stop/restart)
- Monitoring resource

## Lisensi

MIT
