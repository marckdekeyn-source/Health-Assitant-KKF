"""
Sound Alert Module
Modul untuk memainkan suara notifikasi
"""
import os
import sys
from typing import Optional

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️  pygame tidak terinstall. Sound alert akan dinonaktifkan.")
    print("   Install dengan: pip install pygame")


class SoundAlert:
    """Kelas untuk mengelola sound alert"""
    
    def __init__(self, sound_dir: str = "sounds", enabled: bool = True, volume: float = 0.8):
        """
        Args:
            sound_dir: Direktori berisi file suara
            enabled: Enable/disable sound
            volume: Volume (0.0 - 1.0)
        """
        self.sound_dir = sound_dir
        self.enabled = enabled and PYGAME_AVAILABLE
        self.volume = max(0.0, min(1.0, volume))
        
        if self.enabled:
            try:
                pygame.mixer.init()
                print("✓ Sound system initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize sound: {e}")
                self.enabled = False
        
        # Generate default sounds jika tidak ada
        self._ensure_sounds_exist()
    
    def _ensure_sounds_exist(self):
        """Membuat direktori sounds dan generate suara default jika perlu"""
        os.makedirs(self.sound_dir, exist_ok=True)
        
        # Path untuk file suara
        self.water_sound = os.path.join(self.sound_dir, "peaceful-piano-loop-6903.wav")
        self.break_sound = os.path.join(self.sound_dir, "relaxing-guitar-loop-v5-245859.wav")
        self.success_sound = os.path.join(self.sound_dir, "soft-harmonic-breath-short-450972.wav")
        
        # Generate simple beep jika file tidak ada
        if self.enabled and not os.path.exists(self.water_sound):
            self._generate_beep(self.water_sound, frequency=800, duration=5.0)
        
        if self.enabled and not os.path.exists(self.break_sound):
            self._generate_beep(self.break_sound, frequency=600, duration=5.0)
        
        if self.enabled and not os.path.exists(self.success_sound):
            self._generate_beep(self.success_sound, frequency=1000, duration=5.0)
    
    def _generate_beep(self, filepath: str, frequency: int = 800, 
                       duration: float = 5.3, sample_rate: int = 22050):
        """
        Generate simple beep sound
        
        Args:
            filepath: Path untuk save file
            frequency: Frekuensi dalam Hz
            duration: Durasi dalam detik
            sample_rate: Sample rate
        """
        try:
            import numpy as np
            import wave
            import struct
            
            num_samples = int(sample_rate * duration)
            
            # Generate sine wave
            samples = []
            for i in range(num_samples):
                value = int(32767.0 * 0.5 * np.sin(2 * np.pi * frequency * i / sample_rate))
                samples.append(value)
            
            # Write to WAV file
            with wave.open(filepath, 'w') as wav_file:
                wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
                for sample in samples:
                    wav_file.writeframes(struct.pack('h', sample))
            
            print(f"✓ Generated sound: {filepath}")
        except Exception as e:
            print(f"⚠️  Failed to generate beep: {e}")
    
    def play_water_reminder(self):
        """Mainkan suara pengingat minum air"""
        if self.enabled:
            self._play_sound(self.water_sound)
    
    def play_break_reminder(self):
        """Mainkan suara pengingat istirahat"""
        if self.enabled:
            self._play_sound(self.break_sound)
    
    def play_success(self):
        """Mainkan suara sukses"""
        if self.enabled:
            self._play_sound(self.success_sound)
    
    def _play_sound(self, sound_file: str):
        """
        Internal method untuk memainkan file suara
        
        Args:
            sound_file: Path ke file suara
        """
        if not self.enabled:
            return
        
        if not os.path.exists(sound_file):
            print(f"⚠️  Sound file not found: {sound_file}")
            return
        
        try:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(self.volume)
            sound.play()
        except Exception as e:
            print(f"⚠️  Failed to play sound: {e}")
    
    def set_volume(self, volume: float):
        """
        Set volume (0.0 - 1.0)
        
        Args:
            volume: Volume level
        """
        self.volume = max(0.0, min(1.0, volume))
    
    def toggle_enabled(self):
        """Toggle sound on/off"""
        if PYGAME_AVAILABLE:
            self.enabled = not self.enabled
            status = "enabled" if self.enabled else "disabled"
            print(f"Sound alert {status}")
            return self.enabled
        else:
            print("pygame not available")
            return False
    
    def cleanup(self):
        """Cleanup pygame mixer"""
        if self.enabled:
            try:
                pygame.mixer.quit()
            except:
                pass


# Function untuk test sound
def test_sounds():
    """Test semua suara"""
    print("\n🔊 Testing sound alerts...")
    sound = SoundAlert(enabled=True)
    
    if not sound.enabled:
        print("Sound is disabled or pygame not available")
        return
    
    import time
    
    print("Playing water reminder...")
    sound.play_water_reminder()
    time.sleep(5)
    
    print("Playing break reminder...")
    sound.play_break_reminder()
    time.sleep(5)
    
    print("Playing success sound...")
    sound.play_success()
    time.sleep(5)
    
    print("✓ Sound test complete")
    sound.cleanup()


if __name__ == "__main__":
    test_sounds()