# Virtualizor Telegram Bot

[![Quality Gate Status](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=alert_status&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Lines of Code](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=ncloc&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Maintainability Rating](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=software_quality_maintainability_rating&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)
[![Security Rating](https://sonarqube.rizzcode.id/api/project_badges/measure?project=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c&metric=software_quality_security_rating&token=sqb_bde1cc989cafdc5cb6d0955492f0334bf180a1f8)](https://sonarqube.rizzcode.id/dashboard?id=iam-rizz_virtualizor-telegram-bot_ac4d47ff-1899-4b16-b098-fe634c597e6c)

### Rekomendasi VPS, NAT VPS (Virtualizor) & Hosting

<div align="center">

Butuh VPS untuk testing script ini? **[HostData.id](https://hostdata.id)** menyediakan berbagai pilihan hosting terpercaya dengan harga terjangkau.

[![HostData.id](https://img.shields.io/badge/HostData.id-VPS%20Terpercaya-FF6B35?style=flat&logo=server&logoColor=white)](https://hostdata.id) 
[![NAT VPS](https://img.shields.io/badge/NAT%20VPS-Mulai%2015K/bulan-00C851?style=flat)](https://hostdata.id/nat-vps)
[![VPS Indonesia](https://img.shields.io/badge/VPS%20Indonesia-Mulai%20200K/bulan-007ACC?style=flat&logo=server)](https://hostdata.id/vps-indonesia)
[![Dedicated Server](https://img.shields.io/badge/Dedicated%20Server-Enterprise%20Ready-8B5CF6?style=flat&logo=server)](https://hostdata.id/dedicated-server)

</div>

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

## Instalasi

1. Clone repository:
```bash
git clone https://github.com/iam-rizz/virtualizor-telegram-bot.git
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
ALLOWED_USER_IDS=123456789,987654321
```

6. Jalankan bot:
```bash
python main.py
```

## Konfigurasi

| Variable | Deskripsi |
|----------|-----------|
| BOT_TOKEN | Token bot Telegram dari @BotFather |
| ALLOWED_USER_IDS | ID Telegram dipisah koma (contoh: 123456789,987654321) |
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
    - Pilih API (jika lebih dari satu)
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
║   Virtualizor Telegram Bot v1.0.4         ║
║   ─────────────────────────────────────   ║
║   VM Management via Telegram              ║
║   github.com/iam-rizz                     ║
╚═══════════════════════════════════════════╝

22:30:15    INFO bot          Starting bot...
22:30:15    INFO bot          Configuration loaded
22:30:15    INFO bot          Authorized users: [123456789, 987654321]
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

## Author

- GitHub: [@iam-rizz](https://github.com/iam-rizz)
- Telegram: [@rizzid03](https://t.me/rizzid03)
- Forum: [IPv6Indonesia](https://t.me/IPv6Indonesia)

## Lisensi

MIT
