"""
Health Assistant - Main Application
Aplikasi pengingat minum air dan istirahat dengan fitur adaptif
"""
import json
import os
import sys
import threading
import time
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, messagebox, simpledialog
from typing import Dict

# Import modul lokal
from health_calculator import HealthCalculator, AdaptiveBreakManager, WaterIntakeTracker
from activity_logger import ActivityLogger
from sound_alert import SoundAlert
from telegram_notifier import TelegramNotifier


class HealthAssistantApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Health Assistant - Stay Healthy! 💙")
        self.root.geometry("800x700")
        self.root.resizable(False, False)
        
        # Load konfigurasi
        self.config_file = "config/config.json"
        self.config = self.load_config()
        
        # Initialize komponen
        self.logger = ActivityLogger("logs")
        self.sound = SoundAlert(
            "sounds", 
            enabled=self.config['sound']['enabled'],
            volume=self.config['sound']['volume']
        )
        
        # Telegram setup with safe boolean conversion
        tg_config = self.config['telegram']
        # Ensure enabled is boolean
        tg_enabled = tg_config.get('enabled', False)
        if not isinstance(tg_enabled, bool):
            tg_enabled = str(tg_enabled).lower() in ['true', '1', 'yes']
        
        self.telegram = TelegramNotifier(
            bot_token=tg_config.get('bot_token', ''),
            chat_id=tg_config.get('chat_id', ''),
            enabled=tg_enabled
        )
        
        # Health components
        profile = self.config['user_profile']
        self.water_tracker = WaterIntakeTracker(profile['daily_water_target_ml'])
        
        pomo = self.config['pomodoro']
        self.break_manager = AdaptiveBreakManager(
            work_duration=pomo['work_duration_minutes'],
            short_break=pomo['short_break_minutes'],
            long_break=pomo['long_break_minutes'],
            sessions_before_long=pomo['sessions_before_long_break']
        )
        
        # Status aplikasi
        self.is_session_active = False
        self.reminder_thread = None
        self.stop_reminder = False
        self.last_water_reminder = datetime.now()
        self.last_break_check = datetime.now()
        
        # Setup UI
        self.setup_ui()
        
        # Start reminder thread
        self.start_reminder_thread()
        
        # Log app start
        self.logger.log_event("APP_START", "Health Assistant started", "Running")
        
        print("\n✓ Health Assistant started successfully!")
        print(f"  Water target: {profile['daily_water_target_ml']}ml")
        print(f"  Activity level: {profile['activity_level']}")
        print(f"  Sound: {'ON' if self.sound.enabled else 'OFF'}")
        print(f"  Telegram: {'ON' if self.telegram.enabled else 'OFF'}\n")
    
    def load_config(self) -> Dict:
        """Load konfigurasi dari file JSON"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config: {e}")
            return self.get_default_config()
    
    def save_config(self):
        """Save konfigurasi ke file JSON"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get_default_config(self) -> Dict:
        """Return konfigurasi default"""
        return {
            "user_profile": {
                "weight_kg": 70,
                "activity_level": "moderate",
                "daily_water_target_ml": 2500
            },
            "telegram": {
                "bot_token": "",
                "chat_id": "",
                "enabled": False
            },
            "sound": {
                "enabled": True,
                "volume": 0.8
            },
            "pomodoro": {
                "work_duration_minutes": 25,
                "short_break_minutes": 5,
                "long_break_minutes": 15,
                "sessions_before_long_break": 4
            }
        }
    
    def setup_ui(self):
        """Setup user interface"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main container
        main_frame = Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header = Label(
            main_frame, 
            text="💧 Health Assistant 💪", 
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        header.pack(pady=(0, 20))
        
        # Notebook untuk tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=BOTH, expand=True)
        
        # Tab 1: Dashboard
        self.dashboard_tab = Frame(notebook, bg='white')
        notebook.add(self.dashboard_tab, text='📊 Dashboard')
        self.setup_dashboard_tab()
        
        # Tab 2: Settings
        self.settings_tab = Frame(notebook, bg='white')
        notebook.add(self.settings_tab, text='⚙️ Settings')
        self.setup_settings_tab()
        
        # Tab 3: Logs
        self.logs_tab = Frame(notebook, bg='white')
        notebook.add(self.logs_tab, text='📝 Activity Logs')
        self.setup_logs_tab()
        
        # Tab 4: About
        self.about_tab = Frame(notebook, bg='white')
        notebook.add(self.about_tab, text='ℹ️ About')
        self.setup_about_tab()
    
    def setup_dashboard_tab(self):
        """Setup dashboard tab"""
        # Water tracking section
        water_frame = LabelFrame(
            self.dashboard_tab, 
            text="💧 Water Intake Tracking",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=20,
            pady=20
        )
        water_frame.pack(fill=X, padx=20, pady=10)
        
        self.water_progress_label = Label(
            water_frame,
            text="0ml / 2500ml (0.0%)",
            font=('Arial', 14),
            bg='white'
        )
        self.water_progress_label.pack()
        
        self.water_progress_bar = ttk.Progressbar(
            water_frame,
            length=400,
            mode='determinate'
        )
        self.water_progress_bar.pack(pady=10)
        
        water_buttons = Frame(water_frame, bg='white')
        water_buttons.pack()
        
        Button(
            water_buttons,
            text="Add 250ml",
            command=lambda: self.add_water_intake(250),
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        ).pack(side=LEFT, padx=5)
        
        Button(
            water_buttons,
            text="Add 500ml",
            command=lambda: self.add_water_intake(500),
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        ).pack(side=LEFT, padx=5)
        
        Button(
            water_buttons,
            text="Custom Amount",
            command=self.add_custom_water,
            bg='#2ecc71',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        ).pack(side=LEFT, padx=5)
        
        # Work session section
        session_frame = LabelFrame(
            self.dashboard_tab,
            text="⏰ Work Session (Pomodoro)",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=20,
            pady=20
        )
        session_frame.pack(fill=X, padx=20, pady=10)
        
        self.session_status_label = Label(
            session_frame,
            text="Session: Inactive",
            font=('Arial', 14),
            bg='white'
        )
        self.session_status_label.pack()
        
        self.session_stats_label = Label(
            session_frame,
            text="Sessions: 0 | Work time: 0.0 min",
            font=('Arial', 11),
            bg='white',
            fg='#7f8c8d'
        )
        self.session_stats_label.pack(pady=5)
        
        self.session_button = Button(
            session_frame,
            text="▶️ Start Session",
            command=self.toggle_session,
            bg='#27ae60',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=30,
            pady=10
        )
        self.session_button.pack(pady=10)
        
        # Quick stats
        stats_frame = LabelFrame(
            self.dashboard_tab,
            text="📈 Today's Statistics",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=20,
            pady=20
        )
        stats_frame.pack(fill=X, padx=20, pady=10)
        
        self.stats_text = Text(
            stats_frame,
            height=6,
            width=60,
            font=('Courier', 10),
            bg='#ecf0f1',
            relief=FLAT
        )
        self.stats_text.pack()
        
        # Update stats button
        Button(
            self.dashboard_tab,
            text="🔄 Refresh Statistics",
            command=self.update_dashboard,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def setup_settings_tab(self):
        """Setup settings tab"""
        # User profile section
        profile_frame = LabelFrame(
            self.settings_tab,
            text="👤 User Profile",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=20,
            pady=20
        )
        profile_frame.pack(fill=X, padx=20, pady=10)
        
        Button(
            profile_frame,
            text="⚙️ Update Profile (Weight & Activity)",
            command=self.update_profile,
            bg='#3498db',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=15,
            pady=5
        ).pack()
        
        # Sound settings
        sound_frame = LabelFrame(
            self.settings_tab,
            text="🔊 Sound Settings",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=20,
            pady=20
        )
        sound_frame.pack(fill=X, padx=20, pady=10)
        
        self.sound_var = BooleanVar(value=self.sound.enabled)
        Checkbutton(
            sound_frame,
            text="Enable Sound Alerts",
            variable=self.sound_var,
            command=self.toggle_sound,
            font=('Arial', 10),
            bg='white'
        ).pack()
        
        Button(
            sound_frame,
            text="🔊 Test Sound",
            command=self.sound.play_success,
            bg='#9b59b6',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        ).pack(pady=5)
        
        # Telegram settings
        telegram_frame = LabelFrame(
            self.settings_tab,
            text="📱 Telegram Integration",
            font=('Arial', 12, 'bold'),
            bg='white',
            padx=20,
            pady=20
        )
        telegram_frame.pack(fill=X, padx=20, pady=10)
        
        # Safe boolean conversion
        telegram_enabled = bool(self.telegram.enabled) if isinstance(self.telegram.enabled, bool) else False
        self.telegram_var = BooleanVar(value=telegram_enabled)
        Checkbutton(
            telegram_frame,
            text="Enable Telegram Notifications",
            variable=self.telegram_var,
            command=self.toggle_telegram,
            font=('Arial', 10),
            bg='white'
        ).pack()
        
        Button(
            telegram_frame,
            text="⚙️ Configure Telegram Bot",
            command=self.configure_telegram,
            bg='#0088cc',
            fg='white',
            font=('Arial', 10),
            padx=15,
            pady=5
        ).pack(pady=5)
    
    def setup_logs_tab(self):
        """Setup logs tab"""
        Label(
            self.logs_tab,
            text="Recent Activity Logs",
            font=('Arial', 14, 'bold'),
            bg='white'
        ).pack(pady=20)
        
        # Scrollable text area
        scroll_frame = Frame(self.logs_tab, bg='white')
        scroll_frame.pack(fill=BOTH, expand=True, padx=20, pady=10)
        
        scrollbar = Scrollbar(scroll_frame)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        self.logs_text = Text(
            scroll_frame,
            font=('Courier', 9),
            bg='#ecf0f1',
            yscrollcommand=scrollbar.set,
            wrap=WORD
        )
        self.logs_text.pack(fill=BOTH, expand=True)
        scrollbar.config(command=self.logs_text.yview)
        
        Button(
            self.logs_tab,
            text="🔄 Refresh Logs",
            command=self.load_logs,
            bg='#95a5a6',
            fg='white',
            font=('Arial', 10, 'bold'),
            padx=20,
            pady=5
        ).pack(pady=10)
    
    def setup_about_tab(self):
        """Setup about tab"""
        about_text = """
        💙 Health Assistant v1.0
        
        Aplikasi pengingat kesehatan cerdas untuk membantu Anda:
        • Menjaga hidrasi dengan pengingat minum air adaptif
        • Istirahat teratur dengan teknik Pomodoro
        • Tracking aktivitas harian
        • Notifikasi suara dan Telegram
        
        Fitur Utama:
        ✓ Smart water intake calculator
        ✓ Adaptive break timing
        ✓ Activity logging (CSV)
        ✓ Sound alerts
        ✓ Telegram integration
        
        Dibuat dengan ❤️ menggunakan Python
        Teknologi: tkinter, pygame, requests
        
        © 2026 Health Assistant
        """
        
        Label(
            self.about_tab,
            text=about_text,
            font=('Arial', 11),
            bg='white',
            justify=LEFT,
            padx=40,
            pady=40
        ).pack()
    
    def start_reminder_thread(self):
        """Start background thread untuk reminder"""
        self.stop_reminder = False
        self.reminder_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.reminder_thread.start()
    
    def reminder_loop(self):
        """Loop untuk check dan kirim reminder"""
        water_reminder_interval = 60  # setting waktu reminders
        
        while not self.stop_reminder:
            try:
                now = datetime.now()
                
                # Check water reminder
                seconds_since_water = (now - self.last_water_reminder).total_seconds()
                if seconds_since_water >= water_reminder_interval:
                    self.send_water_reminder()
                    self.last_water_reminder = now
                
                # Check break reminder (hanya jika session aktif)
                if self.is_session_active:
                    minutes_since_break = (now - self.last_break_check).total_seconds() / 60
                    if self.break_manager.should_remind_break(int(minutes_since_break)):
                        self.send_break_reminder()
                        self.last_break_check = now
                
                # Sleep 60 detik sebelum check lagi
                time.sleep(60)
            
            except Exception as e:
                print(f"Error in reminder loop: {e}")
                time.sleep(60)
    
    def send_water_reminder(self):
        """Kirim pengingat minum air"""
        remaining = self.water_tracker.get_remaining()
        amount = min(250, remaining)
        progress = self.water_tracker.get_progress_percentage()
        
        # Play sound
        self.sound.play_water_reminder()
        
        # Show notification
        self.root.after(0, lambda: messagebox.showinfo(
            "💧 Pengingat Minum Air",
            f"Saatnya minum air!\n\nTarget: {amount}ml\nProgress: {progress:.1f}%"
        ))
        
        # Send Telegram
        if self.telegram.enabled:
            success = self.telegram.send_water_reminder(amount, progress)
            self.logger.log_telegram_notification(
                f"Water reminder: {amount}ml",
                success
            )
        
        # Log
        self.logger.log_water_reminder(amount, False)
    
    def send_break_reminder(self):
        """Kirim pengingat istirahat"""
        duration, break_type = self.break_manager.get_recommended_break_duration()
        sessions = self.break_manager.current_session
        
        # Play sound
        self.sound.play_break_reminder()
        
        # Show notification
        break_label = "Istirahat Pendek" if break_type == "short" else "Istirahat Panjang"
        self.root.after(0, lambda: messagebox.showinfo(
            "⏰ Pengingat Istirahat",
            f"{break_label}\n\nDurasi: {duration} menit\nSesi selesai: {sessions}"
        ))
        
        # Send Telegram
        if self.telegram.enabled:
            success = self.telegram.send_break_reminder(break_type, duration, sessions)
            self.logger.log_telegram_notification(
                f"Break reminder: {break_type}",
                success
            )
        
        # Log
        self.logger.log_break_reminder(break_type, duration, False)
    
    def add_water_intake(self, amount_ml: int):
        """Tambah konsumsi air"""
        self.water_tracker.add_intake(amount_ml)
        self.logger.log_water_intake(amount_ml)
        self.sound.play_success()
        self.update_dashboard()
        
        # Check achievement
        progress = self.water_tracker.get_progress_percentage()
        if progress >= 100:
            messagebox.showinfo(
                "🎉 Achievement!",
                "Selamat! Target air harian tercapai! 💧"
            )
            if self.telegram.enabled:
                self.telegram.send_achievement("Target air harian tercapai! 🎉💧")
    
    def add_custom_water(self):
        """Tambah air dengan jumlah custom"""
        amount = simpledialog.askinteger(
            "Custom Amount",
            "Masukkan jumlah air (ml):",
            minvalue=1,
            maxvalue=2000
        )
        if amount:
            self.add_water_intake(amount)
    
    def toggle_session(self):
        """Toggle work session on/off"""
        if not self.is_session_active:
            # Start session
            self.is_session_active = True
            self.break_manager.start_session()
            self.logger.log_session_start()
            self.last_break_check = datetime.now()
            
            self.session_button.config(
                text="⏸️ End Session",
                bg='#e74c3c'
            )
            self.session_status_label.config(
                text="Session: Active 🟢",
                fg='#27ae60'
            )
        else:
            # End session
            self.is_session_active = False
            self.break_manager.end_session()
            
            duration = self.break_manager.total_work_time
            self.logger.log_session_end(duration)
            
            self.session_button.config(
                text="▶️ Start Session",
                bg='#27ae60'
            )
            self.session_status_label.config(
                text="Session: Inactive 🔴",
                fg='#e74c3c'
            )
        
        self.update_dashboard()
    
    def update_dashboard(self):
        """Update dashboard statistics"""
        # Water stats
        water_stats = self.water_tracker.get_stats()
        self.water_progress_label.config(
            text=f"{water_stats['consumed_ml']}ml / {water_stats['target_ml']}ml ({water_stats['progress_percent']:.1f}%)"
        )
        self.water_progress_bar['value'] = water_stats['progress_percent']
        
        # Session stats
        break_stats = self.break_manager.get_stats()
        self.session_stats_label.config(
            text=f"Sessions: {break_stats['sessions_completed']} | Work time: {break_stats['total_work_time_minutes']:.1f} min"
        )
        
        # Log summary
        log_stats = self.logger.get_today_summary()
        
        stats_text = f"""
Today's Activity Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💧 Water: {water_stats['consumed_ml']}ml / {water_stats['target_ml']}ml ({water_stats['progress_percent']:.1f}%)
⏰ Sessions: {break_stats['sessions_completed']} completed
📊 Events: {log_stats['total_events']} logged
📝 Water reminders: {log_stats['water_reminders']}
⏸️  Break reminders: {log_stats['break_reminders']}
"""
        
        self.stats_text.delete('1.0', END)
        self.stats_text.insert('1.0', stats_text.strip())
    
    def load_logs(self):
        """Load dan tampilkan logs hari ini"""
        today = datetime.now().strftime("%Y-%m-%d")
        logs = self.logger.get_logs_for_date(today)
        
        self.logs_text.delete('1.0', END)
        
        if not logs:
            self.logs_text.insert('1.0', "No logs for today yet.")
            return
        
        log_text = f"Activity Logs for {today}\n"
        log_text += "=" * 70 + "\n\n"
        
        for log in logs[-20:]:  # Show last 20 entries
            log_text += f"[{log['Timestamp']}] {log['Event Type']}\n"
            log_text += f"  → {log['Description']}\n"
            if log['Action Taken'] != 'None':
                log_text += f"  ✓ {log['Action Taken']}\n"
            log_text += "\n"
        
        self.logs_text.insert('1.0', log_text)
    
    def update_profile(self):
        """Update user profile"""
        # Ask weight
        weight = simpledialog.askfloat(
            "Update Profile",
            "Masukkan berat badan (kg):",
            minvalue=30,
            maxvalue=200
        )
        
        if not weight:
            return
        
        # Ask activity level
        activity_window = Toplevel(self.root)
        activity_window.title("Activity Level")
        activity_window.geometry("400x300")
        
        Label(
            activity_window,
            text="Pilih tingkat aktivitas:",
            font=('Arial', 12, 'bold')
        ).pack(pady=20)
        
        activity_var = StringVar(value="moderate")
        
        activities = [
            ("Sedentary (Tidak aktif)", "sedentary"),
            ("Light (Aktivitas ringan)", "light"),
            ("Moderate (Aktivitas sedang)", "moderate"),
            ("Active (Aktif)", "active"),
            ("Very Active (Sangat aktif)", "very_active")
        ]
        
        for text, value in activities:
            Radiobutton(
                activity_window,
                text=text,
                variable=activity_var,
                value=value,
                font=('Arial', 10)
            ).pack(anchor=W, padx=40)
        
        def save_profile():
            activity = activity_var.get()
            
            # Calculate new target
            new_target = HealthCalculator.calculate_daily_water_target(weight, activity)
            
            # Update config
            self.config['user_profile']['weight_kg'] = weight
            self.config['user_profile']['activity_level'] = activity
            self.config['user_profile']['daily_water_target_ml'] = new_target
            self.save_config()
            
            # Update tracker
            self.water_tracker.daily_target = new_target
            
            messagebox.showinfo(
                "Profile Updated",
                f"Profile berhasil diupdate!\n\nNew water target: {new_target}ml/day"
            )
            
            activity_window.destroy()
            self.update_dashboard()
        
        Button(
            activity_window,
            text="Save Profile",
            command=save_profile,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=30,
            pady=10
        ).pack(pady=20)
    
    def toggle_sound(self):
        """Toggle sound on/off"""
        self.sound.enabled = self.sound_var.get()
        self.config['sound']['enabled'] = self.sound.enabled
        self.save_config()
    
    def toggle_telegram(self):
        """Toggle Telegram on/off"""
        if self.telegram.bot_token and self.telegram.chat_id:
            self.telegram.enabled = self.telegram_var.get()
            self.config['telegram']['enabled'] = self.telegram.enabled
            self.save_config()
        else:
            self.telegram_var.set(False)
            messagebox.showwarning(
                "Telegram Not Configured",
                "Please configure Telegram bot first!"
            )
    
    def configure_telegram(self):
        """Configure Telegram bot"""
        config_window = Toplevel(self.root)
        config_window.title("Configure Telegram")
        config_window.geometry("500x350")
        
        Label(
            config_window,
            text="Telegram Bot Configuration",
            font=('Arial', 14, 'bold')
        ).pack(pady=20)
        
        # Bot token
        Label(config_window, text="Bot Token:", font=('Arial', 10)).pack()
        token_entry = Entry(config_window, width=50)
        token_entry.pack(pady=5)
        token_entry.insert(0, self.telegram.bot_token)
        
        # Chat ID
        Label(config_window, text="Chat ID:", font=('Arial', 10)).pack(pady=(10, 0))
        chatid_entry = Entry(config_window, width=50)
        chatid_entry.pack(pady=5)
        chatid_entry.insert(0, self.telegram.chat_id)
        
        # Instructions
        instructions = """
How to get these values:
1. Create bot with @BotFather, get TOKEN
2. Send message to your bot
3. Get chat ID from @userinfobot
        """
        Label(
            config_window,
            text=instructions,
            font=('Arial', 9),
            fg='#7f8c8d',
            justify=LEFT
        ).pack(pady=10)
        
        def save_telegram_config():
            token = token_entry.get().strip()
            chat_id = chatid_entry.get().strip()
            
            if not token or not chat_id:
                messagebox.showerror("Error", "Please fill both fields!")
                return
            
            # Update config
            self.config['telegram']['bot_token'] = token
            self.config['telegram']['chat_id'] = chat_id
            self.save_config()
            
            # Reconfigure telegram
            self.telegram.configure(token, chat_id)
            
            if self.telegram.enabled:
                # Test send
                success = self.telegram.send_message("✓ Telegram configured successfully!")
                if success:
                    messagebox.showinfo("Success", "Telegram configured and tested!")
                else:
                    messagebox.showwarning("Warning", "Configured but test message failed")
            else:
                messagebox.showinfo("Saved", "Configuration saved!")
            
            config_window.destroy()
        
        Button(
            config_window,
            text="Save Configuration",
            command=save_telegram_config,
            bg='#0088cc',
            fg='white',
            font=('Arial', 11, 'bold'),
            padx=30,
            pady=10
        ).pack(pady=20)
    
    def on_closing(self):
        """Handle window close"""
        # Generate summary
        water_stats = self.water_tracker.get_stats()
        break_stats = self.break_manager.get_stats()
        summary = self.logger.generate_daily_summary(water_stats, break_stats)
        
        print("\n" + summary)
        
        # Send summary via Telegram
        if self.telegram.enabled:
            self.telegram.send_daily_summary(summary)
        
        # Stop reminder thread
        self.stop_reminder = True
        
        # Cleanup
        self.sound.cleanup()
        
        # Log app stop
        self.logger.log_event("APP_STOP", "Health Assistant stopped", "Exiting")
        
        self.root.destroy()


def main():
    """Main function"""
    print("\n" + "="*60)
    print("🏥 HEALTH ASSISTANT - Stay Healthy! 💙")
    print("="*60)
    
    root = Tk()
    app = HealthAssistantApp(root)
    
    # Handle window close
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Start main loop
    root.mainloop()


if __name__ == "__main__":
    main()