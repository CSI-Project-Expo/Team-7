"""
voice_alert.py - Using Pre-recorded WAV files (NO GLITCHES)
"""

import pygame
import os
import time

SOUNDS_FOLDER = "assets/sounds"

class VoiceAlert:
    
    def __init__(self, enabled=True):
        self.enabled = enabled
        self.sounds = {}
        self.last_play_time = 0
        self.min_gap = 1.5
        
        self._load_sounds()
    
    def _load_sounds(self):
        sound_files = {
            'game_start': 'game_start.wav',
            'wave_start': 'wave_start.wav',
            'wave_complete': 'wave_complete.wav',
            'threat': 'threat.wav',
            'blocked': 'blocked.wav',
            'critical': 'critical.wav',
            'health_low': 'health_low.wav',
            'game_over': 'game_over.wav',
            'auto_on': 'auto_on.wav',
            'auto_off': 'auto_off.wav',
            'combo': 'combo.wav',
            'achievement': 'achievement.wav'
        }
        
        try:
            pygame.mixer.init()
        except:
            self.enabled = False
            print("[VOICE] ⚠️ Audio system not available")
            return
        
        for name, filename in sound_files.items():
            filepath = os.path.join(SOUNDS_FOLDER, filename)
            if os.path.exists(filepath):
                try:
                    self.sounds[name] = pygame.mixer.Sound(filepath)
                    print(f"[VOICE] ✅ Loaded: {filename}")
                except:
                    pass
        
        if self.sounds:
            print(f"[VOICE] ✅ {len(self.sounds)} sounds loaded")
        else:
            print("[VOICE] ⚠️ No sounds found")
            self.enabled = False
    
    def _play(self, sound_name):
        if not self.enabled:
            return
        
        if time.time() - self.last_play_time < self.min_gap:
            return
        
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                self.last_play_time = time.time()
            except:
                pass
    
    def alert_game_start(self):
        self._play('game_start')
    
    def alert_wave_start(self, wave_number):
        self._play('wave_start')
    
    def alert_wave_complete(self, wave_number):
        self._play('wave_complete')
    
    def alert_threat_detected(self):
        self._play('threat')
    
    def alert_ip_blocked(self):
        self._play('blocked')
    
    def alert_critical(self):
        self._play('critical')
    
    def alert_health_low(self):
        self._play('health_low')
    
    def alert_auto_defense(self, status):
        if status:
            self._play('auto_on')
        else:
            self._play('auto_off')
    
    def alert_game_over(self):
        self._play('game_over')
    
    def alert_achievement(self, name):
        self._play('achievement')
    
    def alert_combo(self, combo):
        if combo >= 5:
            self._play('combo')
    
    def set_enabled(self, enabled):
        self.enabled = enabled


def get_voice_alert():
    return VoiceAlert()


if __name__ == "__main__":
    import time
    
    pygame.init()
    
    voice = VoiceAlert()
    
    print("Testing sounds...")
    voice.alert_game_start()
    time.sleep(2)
    voice.alert_wave_start(1)
    time.sleep(2)
    voice.alert_threat_detected()
    time.sleep(2)
    
    print("Done!")
    pygame.quit()
