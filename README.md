# 🏥 Health Assistant - Stay Healthy! 💙

Aplikasi Python desktop untuk membantu Anda menjaga kesehatan dengan pengingat cerdas untuk minum air dan istirahat teratur.

## ✨ Fitur Utama

### 1. 💧 Pengingat Minum Air Cerdas (Smart Water Reminders)
- **Kalkulasi Target Berbasis Profil**: Menghitung kebutuhan air harian berdasarkan berat badan dan tingkat aktivitas menggunakan formula kesehatan yang teruji
- **Pengingat Adaptif**: Interval pengingat yang menyesuaikan dengan progress harian Anda
- **Tracking Real-time**: Monitor konsumsi air Anda sepanjang hari dengan progress bar visual

### 2. ⏰ Sistem Istirahat Adaptif (Adaptive Break Timing)
- **Teknik Pomodoro**: Implementasi sistem Pomodoro dengan durasi kerja dan istirahat yang dapat dikustomisasi
- **Istirahat Cerdas**: Durasi istirahat otomatis menyesuaikan dengan beban kerja
  - Setelah 2 jam kerja tanpa henti → istirahat lebih lama
  - 4 sesi selesai → long break otomatis
- **Tracking Sesi Kerja**: Catat semua sesi kerja Anda dengan statistik lengkap

### 3. 📝 Log Aktivitas Harian
- **CSV Logging**: Semua aktivitas tercatat otomatis dalam format CSV yang mudah dianalisis
- **Ringkasan Harian**: Generate summary harian dalam format TXT
- **Statistik Lengkap**: Lihat semua event, reminder, dan response Anda

### 4. 🔊 Sound Alert
- **Notifikasi Suara**: Alert suara yang berbeda untuk setiap jenis reminder
- **Auto-generate**: Sistem otomatis generate file WAV jika belum ada
- **Customizable**: Volume dapat disesuaikan dan dapat di-toggle on/off

### 5. 📱 Integrasi Telegram
- **Remote Notifications**: Terima notifikasi di smartphone meskipun jauh dari laptop
- **Bot Telegram**: Menggunakan Telegram Bot API
- **Achievement Alerts**: Notifikasi otomatis saat mencapai target harian

## 📋 Requirements

### System Requirements
- Python 3.7+
- Windows/Linux/MacOS
- Internet connection (untuk fitur Telegram)

### Python Dependencies
```
pygame>=2.5.0
requests>=2.31.0
numpy>=1.24.0
```

## 🚀 Instalasi

### 1. Clone atau Download Project
```bash
git clone <repository-url>
cd health_assistant
```

atau download dan extract ZIP file.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

atau install manual:
```bash
pip install pygame requests numpy
```

### 3. Jalankan Aplikasi
```bash
python main.py
```

## ⚙️ Konfigurasi

### Setup Profil User
1. Buka aplikasi
2. Go to **Settings** tab
3. Klik **Update Profile**
4. Masukkan:
   - Berat badan (kg)
   - Tingkat aktivitas (sedentary, light, moderate, active, very_active)
5. Target air harian akan dikalkulasi otomatis

### Setup Telegram Bot (Optional)

#### Langkah 1: Buat Bot Telegram
1. Buka Telegram dan cari **@BotFather**
2. Kirim command: `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Simpan **Bot Token** yang diberikan (format: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Langkah 2: Dapatkan Chat ID
1. Cari **@userinfobot** di Telegram
2. Kirim command: `/start`
3. Bot akan memberikan **Chat ID** Anda (format: `987654321`)

#### Langkah 3: Konfigurasi di Aplikasi
1. Buka aplikasi Health Assistant
2. Go to **Settings** tab
3. Klik **Configure Telegram Bot**
4. Masukkan Bot Token dan Chat ID
5. Klik **Save Configuration**
6. Enable checkbox "Enable Telegram Notifications"

## 📖 Cara Penggunaan

### Dashboard Tab
1. **Water Intake Tracking**:
   - Klik "Add 250ml" atau "Add 500ml" untuk log konsumsi air
   - Gunakan "Custom Amount" untuk jumlah yang berbeda
   - Progress bar menunjukkan pencapaian target harian

2. **Work Session**:
   - Klik "▶️ Start Session" untuk mulai sesi kerja Pomodoro
   - Aplikasi akan mengingatkan Anda untuk istirahat sesuai jadwal
   - Klik "⏸️ End Session" untuk mengakhiri sesi

3. **Statistics**:
   - Lihat ringkasan aktivitas hari ini
   - Klik "🔄 Refresh Statistics" untuk update data

### Settings Tab
- **User Profile**: Update berat badan dan aktivitas
- **Sound Settings**: Enable/disable dan test sound alerts
- **Telegram Integration**: Konfigurasi dan toggle Telegram notifications

### Activity Logs Tab
- Lihat semua aktivitas yang tercatat hari ini
- Klik "🔄 Refresh Logs" untuk update tampilan
- Log disimpan dalam format CSV di folder `logs/`

## 📁 Struktur File

```
health_assistant/
│
├── main.py                    # File utama aplikasi (GUI)
├── health_calculator.py       # Modul kalkulasi kesehatan & Pomodoro
├── activity_logger.py         # Modul logging aktivitas
├── sound_alert.py             # Modul sound alerts
├── telegram_notifier.py       # Modul integrasi Telegram
├── requirements.txt           # Dependencies
├── README.md                  # Dokumentasi
│
├── config/
│   └── config.json           # File konfigurasi user
│
├── logs/
│   ├── activity_log_YYYY-MM-DD.csv  # Log harian (CSV)
│   └── summary.txt                   # Ringkasan harian
│
└── sounds/
    ├── water_reminder.wav    # Sound untuk pengingat air
    ├── break_reminder.wav    # Sound untuk pengingat istirahat
    └── success.wav           # Sound untuk sukses/achievement
```

## 🎯 Fitur Detail

### Smart Water Calculator

Rumus yang digunakan:
```
Target Air Harian (ml) = Berat Badan (kg) × Faktor Aktivitas
```

Faktor Aktivitas:
- **Sedentary** (duduk seharian): 30 ml/kg
- **Light** (aktivitas ringan): 35 ml/kg
- **Moderate** (aktivitas sedang): 40 ml/kg
- **Active** (aktif berolahraga): 45 ml/kg
- **Very Active** (sangat aktif): 50 ml/kg

Contoh: Berat 70kg dengan aktivitas moderate = 70 × 40 = 2800ml/hari

### Adaptive Break System

**Pomodoro Standard:**
- Work: 25 menit
- Short break: 5 menit
- Long break: 15 menit
- Long break setelah 4 sesi

**Adaptive Logic:**
- Jika total work time > 120 menit tanpa break → trigger long break
- Break duration menyesuaikan dengan beban kerja
- Statistik tracking untuk analisis produktivitas

### CSV Log Format

File: `logs/activity_log_YYYY-MM-DD.csv`

Columns:
- `Timestamp`: Waktu event
- `Event Type`: Jenis event (WATER_REMINDER, BREAK_REMINDER, dll)
- `Description`: Deskripsi event
- `Action Taken`: Aksi yang diambil user
- `Additional Data`: Data tambahan

Contoh:
```csv
Timestamp,Event Type,Description,Action Taken,Additional Data
2026-01-21 10:30:00,WATER_REMINDER,Reminder to drink 250ml water,Drank water,Amount: 250ml
2026-01-21 11:00:00,WATER_INTAKE,Consumed 250ml water,Logged,Amount: 250ml
```

## 🔧 Troubleshooting

### Masalah: pygame tidak terinstall
```
⚠️  pygame tidak terinstall. Sound alert akan dinonaktifkan.
```

**Solusi:**
```bash
pip install pygame
```

### Masalah: Telegram tidak terkoneksi
```
⚠️  Failed to connect to Telegram bot
```

**Solusi:**
1. Cek koneksi internet
2. Verifikasi Bot Token dan Chat ID benar
3. Pastikan bot sudah distart dengan kirim `/start` ke bot Anda

### Masalah: Sound tidak keluar
**Solusi:**
1. Cek Settings → Sound Settings → pastikan enabled
2. Test sound dengan tombol "🔊 Test Sound"
3. Cek volume sistem
4. Pastikan file sound ada di folder `sounds/`

## 💡 Tips Penggunaan

1. **Untuk Produktivitas Maksimal:**
   - Gunakan fitur Pomodoro secara konsisten
   - Review activity logs setiap akhir hari
   - Sesuaikan durasi work/break dengan ritme Anda

2. **Untuk Hidrasi Optimal:**
   - Update profile jika berat badan atau aktivitas berubah
   - Jangan skip water reminder
   - Monitor progress bar sepanjang hari

3. **Integrasi Telegram:**
   - Sangat berguna saat meeting atau mobile
   - Dapatkan summary harian langsung di HP
   - Achievement notification untuk motivasi

## 🎨 Kustomisasi

### Ubah Interval Pengingat
Edit file `main.py`, cari:
```python
water_reminder_interval = 7200  # 2 jam dalam detik
```
Ubah nilai sesuai kebutuhan (dalam detik).

### Ubah Durasi Pomodoro
Edit file `config/config.json`:
```json
"pomodoro": {
  "work_duration_minutes": 25,
  "short_break_minutes": 5,
  "long_break_minutes": 15,
  "sessions_before_long_break": 4
}
```

### Ubah Sound Files
Replace file WAV di folder `sounds/` dengan file Anda sendiri.

## 📊 Analisis Data

Log CSV dapat dianalisis dengan:
- Microsoft Excel / Google Sheets
- Python pandas
- Power BI / Tableau

Contoh analisis dengan pandas:
```python
import pandas as pd

# Load log
df = pd.read_csv('logs/activity_log_2026-01-21.csv')

# Hitung total water intake
water_logs = df[df['Event Type'] == 'WATER_INTAKE']
total_water = water_logs['Additional Data'].str.extract('(\d+)').astype(int).sum()

print(f"Total water consumed: {total_water}ml")
```

## 🤝 Kontribusi

Project ini adalah contoh pembelajaran. Silakan fork dan modifikasi sesuai kebutuhan Anda!

## 📝 License

Free to use and modify.

## 🙏 Credits

Dibuat dengan ❤️ menggunakan:
- Python 3
- tkinter (GUI)
- pygame (Sound)
- requests (HTTP/Telegram)
- numpy (Sound generation)

## 📧 Support

Jika ada pertanyaan atau masalah, silakan:
1. Cek dokumentasi ini terlebih dahulu
2. Review troubleshooting section
3. Cek console output untuk error messages

---

**Stay Healthy! 💙 Keep Coding! 💻**
