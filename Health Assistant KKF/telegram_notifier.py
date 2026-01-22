"""
Telegram Integration Module
Modul untuk mengirim notifikasi via Telegram
"""
import requests
from typing import Optional


class TelegramNotifier:
    """Kelas untuk mengirim notifikasi via Telegram Bot"""
    
    def __init__(self, bot_token: str = "", chat_id: str = "", enabled: bool = False):
        """
        Args:
            bot_token: Token dari BotFather
            chat_id: Chat ID user
            enabled: Enable/disable Telegram notifications
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.enabled = enabled and bot_token and chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        if self.enabled:
            # Test connection
            if self._test_connection():
                print("✓ Telegram bot connected successfully")
            else:
                print("⚠️  Failed to connect to Telegram bot")
                self.enabled = False
    
    def _test_connection(self) -> bool:
        """Test koneksi ke Telegram API"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Telegram connection error: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Kirim pesan teks ke Telegram
        
        Args:
            message: Pesan yang akan dikirim
            parse_mode: Format parsing (HTML atau Markdown)
            
        Returns:
            True jika berhasil, False jika gagal
        """
        if not self.enabled:
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            return response.status_code == 200
        
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")
            return False
    
    def send_water_reminder(self, amount_ml: int, progress_percent: float) -> bool:
        """
        Kirim pengingat minum air
        
        Args:
            amount_ml: Jumlah air yang harus diminum
            progress_percent: Persentase progress harian
            
        Returns:
            True jika berhasil
        """
        message = f"""
💧 <b>Pengingat Minum Air!</b>

Saatnya minum <b>{amount_ml}ml</b> air 🥤

Progress hari ini: <b>{progress_percent:.1f}%</b>

Jangan lupa jaga hidrasi ya! 💙
"""
        return self.send_message(message.strip())
    
    def send_break_reminder(self, break_type: str, duration_min: int, 
                           sessions_completed: int) -> bool:
        """
        Kirim pengingat istirahat
        
        Args:
            break_type: Tipe istirahat (short/long)
            duration_min: Durasi istirahat
            sessions_completed: Jumlah sesi yang sudah diselesaikan
            
        Returns:
            True jika berhasil
        """
        emoji = "☕" if break_type == "short" else "🌟"
        break_label = "Istirahat Pendek" if break_type == "short" else "Istirahat Panjang"
        
        message = f"""
{emoji} <b>{break_label}</b>

Kamu sudah bekerja keras! Saatnya istirahat <b>{duration_min} menit</b>.

Sesi selesai: <b>{sessions_completed}</b>

Tips: Jauhi layar, regangkan badan, atau jalan-jalan sebentar! 🚶‍♂️
"""
        return self.send_message(message.strip())
    
    def send_daily_summary(self, summary_text: str) -> bool:
        """
        Kirim ringkasan harian
        
        Args:
            summary_text: Text ringkasan
            
        Returns:
            True jika berhasil
        """
        # Convert ke HTML format
        html_message = summary_text.replace("========================================", "━━━━━━━━━━━━━━━━━━━━━━")
        html_message = html_message.replace("DAILY HEALTH ASSISTANT SUMMARY", "<b>📊 RINGKASAN HARIAN</b>")
        
        return self.send_message(f"<pre>{html_message}</pre>", parse_mode="HTML")
    
    def send_achievement(self, achievement: str) -> bool:
        """
        Kirim notifikasi achievement
        
        Args:
            achievement: Deskripsi achievement
            
        Returns:
            True jika berhasil
        """
        message = f"🏆 <b>Achievement Unlocked!</b>\n\n{achievement}"
        return self.send_message(message)
    
    def configure(self, bot_token: str, chat_id: str):
        """
        Konfigurasi ulang bot
        
        Args:
            bot_token: Token bot baru
            chat_id: Chat ID baru
        """
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
        
        if bot_token and chat_id:
            self.enabled = self._test_connection()
        else:
            self.enabled = False
    
    def toggle_enabled(self) -> bool:
        """
        Toggle Telegram notifications on/off
        
        Returns:
            Status enabled saat ini
        """
        if self.bot_token and self.chat_id:
            self.enabled = not self.enabled
            status = "enabled" if self.enabled else "disabled"
            print(f"Telegram notifications {status}")
            return self.enabled
        else:
            print("Telegram not configured. Please set bot_token and chat_id first.")
            return False