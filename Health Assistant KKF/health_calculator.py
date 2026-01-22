"""
Health Calculator Module
Modul untuk menghitung kebutuhan air harian dan mengelola pengingat adaptif
"""
from datetime import datetime, timedelta
from typing import Dict, Tuple


class HealthCalculator:
    """Kelas untuk menghitung kebutuhan kesehatan berdasarkan profil user"""
    
    # Faktor aktivitas untuk perhitungan air
    ACTIVITY_MULTIPLIERS = {
        'sedentary': 30,      # ml per kg berat badan
        'light': 35,
        'moderate': 40,
        'active': 45,
        'very_active': 50
    }
    
    @staticmethod
    def calculate_daily_water_target(weight_kg: float, activity_level: str) -> int:
        """
        Menghitung target air harian berdasarkan berat badan dan aktivitas
        
        Formula: Berat badan (kg) × Faktor aktivitas (ml/kg)
        
        Args:
            weight_kg: Berat badan dalam kilogram
            activity_level: Level aktivitas (sedentary, light, moderate, active, very_active)
            
        Returns:
            Target air harian dalam mililiter
        """
        multiplier = HealthCalculator.ACTIVITY_MULTIPLIERS.get(
            activity_level.lower(), 
            35  # default ke 'light'
        )
        
        return int(weight_kg * multiplier)
    
    @staticmethod
    def calculate_water_per_reminder(daily_target_ml: int, hours_awake: int = 16) -> int:
        """
        Menghitung jumlah air per pengingat
        
        Asumsi: User terjaga 16 jam sehari, pengingat setiap 1-2 jam
        
        Args:
            daily_target_ml: Target air harian dalam ml
            hours_awake: Jam terjaga per hari (default 16)
            
        Returns:
            Jumlah air per pengingat dalam ml
        """
        reminders_per_day = hours_awake // 2  # Pengingat setiap 2 jam
        return daily_target_ml // reminders_per_day
    
    @staticmethod
    def get_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
        """
        Menghitung BMI dan kategorinya
        
        Args:
            weight_kg: Berat badan dalam kg
            height_cm: Tinggi badan dalam cm
            
        Returns:
            Tuple (BMI value, kategori)
        """
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        if bmi < 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"
        
        return round(bmi, 2), category


class AdaptiveBreakManager:
    """Mengelola pengingat istirahat adaptif berdasarkan Pomodoro Technique"""
    
    def __init__(self, work_duration: int = 25, short_break: int = 5, 
                 long_break: int = 15, sessions_before_long: int = 4):
        """
        Inisialisasi manager dengan konfigurasi Pomodoro
        
        Args:
            work_duration: Durasi kerja dalam menit (default 25)
            short_break: Durasi istirahat pendek dalam menit (default 5)
            long_break: Durasi istirahat panjang dalam menit (default 15)
            sessions_before_long: Jumlah sesi sebelum istirahat panjang (default 4)
        """
        self.work_duration = work_duration
        self.short_break = short_break
        self.long_break = long_break
        self.sessions_before_long = sessions_before_long
        
        self.current_session = 0
        self.total_work_time = 0  # dalam menit
        self.last_break_time = None
        self.session_start_time = None
    
    def start_session(self):
        """Memulai sesi kerja baru"""
        self.session_start_time = datetime.now()
    
    def end_session(self):
        """Mengakhiri sesi kerja dan update statistik"""
        if self.session_start_time:
            duration = (datetime.now() - self.session_start_time).total_seconds() / 60
            self.total_work_time += duration
            self.current_session += 1
            self.session_start_time = None
    
    def get_recommended_break_duration(self) -> Tuple[int, str]:
        """
        Menghitung durasi istirahat yang disarankan
        
        Returns:
            Tuple (durasi dalam menit, tipe istirahat)
        """
        # Cek apakah sudah waktunya istirahat panjang
        if self.current_session > 0 and self.current_session % self.sessions_before_long == 0:
            return self.long_break, "long"
        
        # Adaptive: Jika total waktu kerja > 120 menit tanpa istirahat panjang
        if self.total_work_time >= 120:
            return self.long_break, "adaptive_long"
        
        return self.short_break, "short"
    
    def should_remind_break(self, minutes_since_last: int) -> bool:
        """
        Menentukan apakah sudah waktunya mengingatkan istirahat
        
        Args:
            minutes_since_last: Menit sejak istirahat terakhir
            
        Returns:
            True jika perlu reminder istirahat
        """
        return minutes_since_last >= self.work_duration
    
    def take_break(self):
        """Mencatat waktu istirahat"""
        self.last_break_time = datetime.now()
        self.total_work_time = 0  # Reset counter setelah istirahat
    
    def get_stats(self) -> Dict:
        """Mendapatkan statistik sesi kerja"""
        return {
            'sessions_completed': self.current_session,
            'total_work_time_minutes': round(self.total_work_time, 1),
            'next_break_type': self.get_recommended_break_duration()[1]
        }


class WaterIntakeTracker:
    """Melacak konsumsi air harian"""
    
    def __init__(self, daily_target_ml: int):
        """
        Args:
            daily_target_ml: Target air harian dalam ml
        """
        self.daily_target = daily_target_ml
        self.consumed_today = 0
        self.last_intake_time = None
        self.intake_history = []
    
    def add_intake(self, amount_ml: int):
        """
        Menambahkan catatan konsumsi air
        
        Args:
            amount_ml: Jumlah air yang diminum dalam ml
        """
        now = datetime.now()
        self.consumed_today += amount_ml
        self.last_intake_time = now
        self.intake_history.append({
            'timestamp': now,
            'amount_ml': amount_ml
        })
    
    def get_progress_percentage(self) -> float:
        """Mendapatkan persentase progress dari target harian"""
        return min(100, (self.consumed_today / self.daily_target) * 100)
    
    def get_remaining(self) -> int:
        """Mendapatkan sisa target dalam ml"""
        return max(0, self.daily_target - self.consumed_today)
    
    def reset_daily(self):
        """Reset counter harian (panggil setiap hari baru)"""
        self.consumed_today = 0
        self.intake_history = []
    
    def get_stats(self) -> Dict:
        """Mendapatkan statistik konsumsi air"""
        return {
            'consumed_ml': self.consumed_today,
            'target_ml': self.daily_target,
            'remaining_ml': self.get_remaining(),
            'progress_percent': round(self.get_progress_percentage(), 1),
            'intake_count': len(self.intake_history)
        }