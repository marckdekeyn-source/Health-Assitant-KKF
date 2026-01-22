"""
Activity Logger Module
Modul untuk mencatat semua aktivitas dan notifikasi ke file
"""
import csv
import os
from datetime import datetime
from typing import Dict, List


class ActivityLogger:
    """Kelas untuk logging aktivitas harian ke file CSV"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        Args:
            log_dir: Direktori untuk menyimpan file log
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        # File log untuk hari ini
        today = datetime.now().strftime("%Y-%m-%d")
        self.csv_file = os.path.join(log_dir, f"activity_log_{today}.csv")
        self.summary_file = os.path.join(log_dir, "summary.txt")
        
        # Inisialisasi file CSV jika belum ada
        self._initialize_csv()
    
    def _initialize_csv(self):
        """Membuat file CSV dengan header jika belum ada"""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp', 
                    'Event Type', 
                    'Description', 
                    'Action Taken',
                    'Additional Data'
                ])
    
    def log_event(self, event_type: str, description: str, 
                   action_taken: str = "None", additional_data: str = ""):
        """
        Mencatat event ke file CSV
        
        Args:
            event_type: Tipe event (water_reminder, break_reminder, etc)
            description: Deskripsi event
            action_taken: Aksi yang diambil user
            additional_data: Data tambahan dalam format string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                event_type,
                description,
                action_taken,
                additional_data
            ])
    
    def log_water_reminder(self, amount_ml: int, responded: bool = False):
        """Log pengingat minum air"""
        action = "Drank water" if responded else "Ignored"
        self.log_event(
            event_type="WATER_REMINDER",
            description=f"Reminder to drink {amount_ml}ml water",
            action_taken=action,
            additional_data=f"Amount: {amount_ml}ml"
        )
    
    def log_break_reminder(self, break_type: str, duration_min: int, 
                           responded: bool = False):
        """Log pengingat istirahat"""
        action = "Took break" if responded else "Continued working"
        self.log_event(
            event_type="BREAK_REMINDER",
            description=f"{break_type.capitalize()} break reminder ({duration_min} min)",
            action_taken=action,
            additional_data=f"Type: {break_type}, Duration: {duration_min}min"
        )
    
    def log_session_start(self):
        """Log dimulainya sesi kerja"""
        self.log_event(
            event_type="SESSION_START",
            description="Work session started",
            action_taken="Started",
            additional_data=""
        )
    
    def log_session_end(self, duration_min: float):
        """Log berakhirnya sesi kerja"""
        self.log_event(
            event_type="SESSION_END",
            description="Work session ended",
            action_taken="Completed",
            additional_data=f"Duration: {duration_min:.1f} minutes"
        )
    
    def log_water_intake(self, amount_ml: int):
        """Log konsumsi air"""
        self.log_event(
            event_type="WATER_INTAKE",
            description=f"Consumed {amount_ml}ml water",
            action_taken="Logged",
            additional_data=f"Amount: {amount_ml}ml"
        )
    
    def log_telegram_notification(self, message: str, success: bool):
        """Log notifikasi Telegram"""
        action = "Sent" if success else "Failed"
        self.log_event(
            event_type="TELEGRAM_NOTIFICATION",
            description=message,
            action_taken=action,
            additional_data=""
        )
    
    def get_today_summary(self) -> Dict:
        """
        Mendapatkan ringkasan aktivitas hari ini
        
        Returns:
            Dictionary berisi statistik hari ini
        """
        if not os.path.exists(self.csv_file):
            return {
                'total_events': 0,
                'water_reminders': 0,
                'break_reminders': 0,
                'water_intake_count': 0,
                'sessions': 0
            }
        
        stats = {
            'total_events': 0,
            'water_reminders': 0,
            'break_reminders': 0,
            'water_intake_count': 0,
            'sessions': 0,
            'telegram_sent': 0
        }
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stats['total_events'] += 1
                
                event_type = row['Event Type']
                if event_type == 'WATER_REMINDER':
                    stats['water_reminders'] += 1
                elif event_type == 'BREAK_REMINDER':
                    stats['break_reminders'] += 1
                elif event_type == 'WATER_INTAKE':
                    stats['water_intake_count'] += 1
                elif event_type == 'SESSION_START':
                    stats['sessions'] += 1
                elif event_type == 'TELEGRAM_NOTIFICATION' and row['Action Taken'] == 'Sent':
                    stats['telegram_sent'] += 1
        
        return stats
    
    def generate_daily_summary(self, water_stats: Dict, break_stats: Dict):
        """
        Generate summary harian ke file txt
        
        Args:
            water_stats: Statistik konsumsi air
            break_stats: Statistik istirahat/sesi kerja
        """
        event_stats = self.get_today_summary()
        
        summary_text = f"""
========================================
DAILY HEALTH ASSISTANT SUMMARY
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
========================================

📊 EVENT STATISTICS:
- Total Events Logged: {event_stats['total_events']}
- Water Reminders Sent: {event_stats['water_reminders']}
- Break Reminders Sent: {event_stats['break_reminders']}
- Water Intake Logged: {event_stats['water_intake_count']} times
- Work Sessions: {event_stats['sessions']}
- Telegram Notifications: {event_stats['telegram_sent']}

💧 WATER INTAKE:
- Consumed: {water_stats.get('consumed_ml', 0)} ml
- Target: {water_stats.get('target_ml', 0)} ml
- Progress: {water_stats.get('progress_percent', 0):.1f}%
- Remaining: {water_stats.get('remaining_ml', 0)} ml

⏰ WORK & BREAK:
- Sessions Completed: {break_stats.get('sessions_completed', 0)}
- Total Work Time: {break_stats.get('total_work_time_minutes', 0):.1f} minutes
- Next Break Type: {break_stats.get('next_break_type', 'N/A')}

========================================
Log file: {self.csv_file}
========================================
"""
        
        # Tulis ke file summary
        with open(self.summary_file, 'a', encoding='utf-8') as f:
            f.write(summary_text)
        
        return summary_text
    
    def get_logs_for_date(self, date_str: str) -> List[Dict]:
        """
        Mendapatkan semua log untuk tanggal tertentu
        
        Args:
            date_str: Tanggal dalam format YYYY-MM-DD
            
        Returns:
            List of dictionaries berisi log entries
        """
        log_file = os.path.join(self.log_dir, f"activity_log_{date_str}.csv")
        
        if not os.path.exists(log_file):
            return []
        
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                logs.append(dict(row))
        
        return logs