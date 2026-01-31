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
- Daftar VM dengan spesifikasi (vCPU, RAM, Storage, OS)
- Indikator status VM (Running, Stopped, Suspended)
- Detail VM dengan penggunaan resource real-time:
  - Alamat IPv4 dan IPv6
  - Penggunaan RAM, Disk, Bandwidth dengan progress bar
  - Jumlah rule port forwarding
  - OS dan tipe virtualisasi
- Validasi koneksi dengan pesan error detail
- Console logging berwarna dengan banner startup
- Notifikasi auto-update dengan update sekali klik

## Persyaratan

- Python 3.10+
- Token Bot Telegram (dari @BotFather)
- Panel Virtualizor dengan akses API aktif
- Ubuntu/Debian (diuji pada Ubuntu 22.04, Debian 12/13)

## Struktur Project

```
virtualizor-telegram-bot/
├── main.py
├── start.sh              # Script auto-setup dan start
├── update.sh             # Script update dan restart
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
│   └── handlers/
│       ├── base.py
│       ├── api_management.py
│       └── vm_management.py
├── data/
├── requirements.txt
└── .env
```

## Quick Start (Direkomendasikan)

```bash
git clone https://github.com/iam-rizz/virtualizor-telegram-bot.git
cd virtualizor-telegram-bot
chmod +x start.sh update.sh
./start.sh
```

Script akan:
1. Cek dan install dependency Python (python3, python3-venv, pip)
2. Buat virtual environment dan install requirements
3. Buat `.env` dari template (edit dengan kredensial Anda)
4. Jalankan bot dengan PM2 (jika tersedia) atau screen

## Instalasi Manual

1. Clone repository:
```bash
git clone https://github.com/iam-rizz/virtualizor-telegram-bot.git
cd virtualizor-telegram-bot
```

2. Buat virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Buat file `.env`:
```bash
cp .env.example .env
nano .env
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

## Update Bot

### Via Telegram
Ketika versi baru tersedia, tombol "Update Bot" akan muncul di menu utama. Klik untuk update dan restart otomatis.

### Via Command Line
```bash
./update.sh
```

## Konfigurasi

| Variable | Deskripsi |
|----------|-----------|
| BOT_TOKEN | Token bot Telegram dari @BotFather |
| ALLOWED_USER_IDS | ID Telegram dipisah koma (contoh: 123456789,987654321) |
| DATABASE_PATH | Path database SQLite (default: data/bot.db) |

## Manajemen Proses

### Dengan PM2 (Direkomendasikan)
```bash
# Lihat logs
pm2 logs virtualizor-bot

# Restart
pm2 restart virtualizor-bot

# Stop
pm2 stop virtualizor-bot
```

### Dengan Screen
```bash
# Attach ke session
screen -r virtualizor-bot

# Detach
Ctrl+A lalu D

# Stop
screen -S virtualizor-bot -X quit
```

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
  - About
  - Update Bot (jika tersedia)

## Mendapatkan Kredensial

- BOT_TOKEN: Kirim pesan ke @BotFather di Telegram, ketik /newbot
- ALLOWED_USER_ID: Kirim pesan ke @userinfobot di Telegram

## Konfigurasi API

Saat menambahkan API, Anda memerlukan:
1. API URL (contoh: https://panel.example.com:4085/index.php)
2. API Key (dari Virtualizor Admin Panel > Configuration > API Credentials)
3. API Password (dari lokasi yang sama)

## Diuji Pada

- Ubuntu 22.04 LTS
- Ubuntu 24.04 LTS
- Debian 12
- Debian 13

## Keamanan

- Akses single user saja
- Password API disimpan ter-encode
- Pesan user otomatis dihapus
- Koneksi API wajib HTTPS

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
