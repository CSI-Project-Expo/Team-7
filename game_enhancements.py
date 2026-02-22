"""
===========================================================
FILE: game_enhancements.py
PURPOSE: Score system, waves, combos, achievements
FEATURE: Innovative game mechanics
===========================================================
"""

import time
from enum import Enum
from typing import Dict, List, Callable


# ============================================
# WAVE SYSTEM
# ============================================

class WaveSystem:
    """
    Manages attack waves with increasing difficulty.
    Each wave is harder than the last.
    """
    
    def __init__(self):
        """Initialize wave system."""
        
        self.current_wave = 0
        self.wave_active = False
        self.wave_start_time = 0
        self.wave_duration = 30  # seconds per wave
        self.break_duration = 5   # seconds between waves
        self.in_break = False
        self.break_start_time = 0
        
        self.waves_completed = 0
        self.total_waves = 10  # Max waves
        
        # Wave configurations
        self.wave_configs = self._generate_wave_configs()
        
        # Callbacks
        self.on_wave_start = None
        self.on_wave_complete = None
        self.on_break_start = None
        
        print("[WAVE] ✅ Wave System initialized")
    
    def _generate_wave_configs(self) -> List[Dict]:
        """Generate configuration for each wave."""
        
        configs = []
        
        for wave_num in range(1, self.total_waves + 1):
            config = {
                'wave_number': wave_num,
                'spawn_rate': min(0.03 + (wave_num * 0.008), 0.15),  # Faster spawns
                'malicious_chance': min(0.1 + (wave_num * 0.05), 0.6),  # More threats
                'packet_speed_multiplier': 1 + (wave_num * 0.1),  # Faster packets
                'duration': 30 + (wave_num * 5),  # Longer waves
                'boss_wave': wave_num % 5 == 0  # Every 5th wave is boss wave
            }
            configs.append(config)
        
        return configs
    
    def start_game(self):
        """Start the wave system."""
        self.current_wave = 0
        self.wave_active = False
        self.waves_completed = 0
        self._start_break()
    
    def _start_wave(self):
        """Start a new wave."""
        
        self.current_wave += 1
        self.wave_active = True
        self.in_break = False
        self.wave_start_time = time.time()
        
        if self.on_wave_start:
            self.on_wave_start(self.current_wave, self.get_current_config())
    
    def _start_break(self):
        """Start break between waves."""
        
        self.wave_active = False
        self.in_break = True
        self.break_start_time = time.time()
        
        if self.on_break_start and self.current_wave > 0:
            self.on_break_start(self.current_wave)
    
    def _complete_wave(self):
        """Complete current wave."""
        
        self.waves_completed += 1
        self.wave_active = False
        
        if self.on_wave_complete:
            self.on_wave_complete(self.current_wave)
        
        self._start_break()
    
    def update(self) -> Dict:
        """
        Update wave system each frame.
        Returns current wave status.
        """
        
        current_time = time.time()
        
        if self.in_break:
            elapsed = current_time - self.break_start_time
            remaining = max(0, self.break_duration - elapsed)
            
            if elapsed >= self.break_duration:
                if self.current_wave < self.total_waves:
                    self._start_wave()
            
            return {
                'wave_active': False,
                'in_break': True,
                'current_wave': self.current_wave,
                'next_wave': self.current_wave + 1,
                'break_remaining': remaining
            }
        
        elif self.wave_active:
            config = self.get_current_config()
            elapsed = current_time - self.wave_start_time
            duration = config['duration'] if config else self.wave_duration
            remaining = max(0, duration - elapsed)
            
            if elapsed >= duration:
                self._complete_wave()
            
            return {
                'wave_active': True,
                'in_break': False,
                'current_wave': self.current_wave,
                'wave_remaining': remaining,
                'config': config
            }
        
        return {
            'wave_active': False,
            'in_break': False,
            'current_wave': self.current_wave
        }
    
    def get_current_config(self) -> Dict:
        """Get current wave configuration."""
        
        if 0 < self.current_wave <= len(self.wave_configs):
            return self.wave_configs[self.current_wave - 1]
        return None
    
    def get_spawn_rate(self) -> float:
        """Get current spawn rate."""
        
        config = self.get_current_config()
        if config:
            return config['spawn_rate']
        return 0.03
    
    def get_malicious_chance(self) -> float:
        """Get current malicious packet chance."""
        
        config = self.get_current_config()
        if config:
            return config['malicious_chance']
        return 0.15
    
    def is_boss_wave(self) -> bool:
        """Check if current wave is a boss wave."""
        
        config = self.get_current_config()
        if config:
            return config.get('boss_wave', False)
        return False


# ============================================
# SCORE SYSTEM
# ============================================

class ScoreSystem:
    """
    Manages player score with combos and multipliers.
    """
    
    def __init__(self):
        """Initialize score system."""
        
        self.score = 0
        self.high_score = 0
        
        # Combo system
        self.combo = 0
        self.max_combo = 0
        self.combo_timer = 0
        self.combo_timeout = 2.0  # seconds to maintain combo
        self.last_action_time = 0
        
        # Multiplier
        self.multiplier = 1.0
        
        # Score values
        self.points = {
            'block_safe': 5,
            'block_suspicious': 15,
            'block_malicious': 30,
            'wave_complete': 100,
            'wave_complete_bonus': 50,  # Per wave number
            'no_damage_bonus': 200,
            'combo_bonus': 10  # Per combo level
        }
        
        # Statistics
        self.total_blocked = 0
        self.malicious_blocked = 0
        self.suspicious_blocked = 0
        
        # Callbacks
        self.on_score_change = None
        self.on_combo_change = None
        self.on_multiplier_change = None
        
        print("[SCORE] ✅ Score System initialized")
    
    def add_block_score(self, packet_type: str):
        """Add score for blocking a packet."""
        
        current_time = time.time()
        
        # Determine base points
        if packet_type == 'malicious':
            base_points = self.points['block_malicious']
            self.malicious_blocked += 1
        elif packet_type == 'suspicious':
            base_points = self.points['block_suspicious']
            self.suspicious_blocked += 1
        else:
            base_points = self.points['block_safe']
        
        # Update combo
        if current_time - self.last_action_time < self.combo_timeout:
            self.combo += 1
        else:
            self.combo = 1
        
        self.last_action_time = current_time
        
        # Update max combo
        if self.combo > self.max_combo:
            self.max_combo = self.combo
        
        # Calculate multiplier based on combo
        self._update_multiplier()
        
        # Calculate final points
        combo_bonus = self.combo * self.points['combo_bonus']
        total_points = int((base_points + combo_bonus) * self.multiplier)
        
        # Add to score
        self.score += total_points
        self.total_blocked += 1
        
        # Update high score
        if self.score > self.high_score:
            self.high_score = self.score
        
        # Callbacks
        if self.on_score_change:
            self.on_score_change(self.score, total_points)
        
        if self.on_combo_change:
            self.on_combo_change(self.combo)
        
        return total_points
    
    def _update_multiplier(self):
        """Update score multiplier based on combo."""
        
        old_multiplier = self.multiplier
        
        if self.combo >= 20:
            self.multiplier = 3.0
        elif self.combo >= 15:
            self.multiplier = 2.5
        elif self.combo >= 10:
            self.multiplier = 2.0
        elif self.combo >= 5:
            self.multiplier = 1.5
        else:
            self.multiplier = 1.0
        
        if self.multiplier != old_multiplier and self.on_multiplier_change:
            self.on_multiplier_change(self.multiplier)
    
    def add_wave_complete_bonus(self, wave_number: int, no_damage: bool = False):
        """Add bonus for completing a wave."""
        
        bonus = self.points['wave_complete']
        bonus += self.points['wave_complete_bonus'] * wave_number
        
        if no_damage:
            bonus += self.points['no_damage_bonus']
        
        self.score += bonus
        
        if self.on_score_change:
            self.on_score_change(self.score, bonus)
        
        return bonus
    
    def update(self):
        """Update score system each frame."""
        
        current_time = time.time()
        
        # Check combo timeout
        if self.combo > 0 and current_time - self.last_action_time > self.combo_timeout:
            self.combo = 0
            self.multiplier = 1.0
            
            if self.on_combo_change:
                self.on_combo_change(0)
    
    def reset(self):
        """Reset score for new game."""
        
        self.score = 0
        self.combo = 0
        self.multiplier = 1.0
        self.total_blocked = 0
        self.malicious_blocked = 0
        self.suspicious_blocked = 0
    
    def get_stats(self) -> Dict:
        """Get score statistics."""
        
        return {
            'score': self.score,
            'high_score': self.high_score,
            'combo': self.combo,
            'max_combo': self.max_combo,
            'multiplier': self.multiplier,
            'total_blocked': self.total_blocked,
            'malicious_blocked': self.malicious_blocked,
            'suspicious_blocked': self.suspicious_blocked
        }


# ============================================
# ACHIEVEMENT SYSTEM
# ============================================

class Achievement:
    """Represents a single achievement."""
    
    def __init__(self, id: str, name: str, description: str, icon: str = "🏆"):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.unlocked = False
        self.unlock_time = None
    
    def unlock(self):
        """Unlock this achievement."""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_time = time.time()
            return True
        return False


class AchievementSystem:
    """
    Manages player achievements.
    """
    
    def __init__(self):
        """Initialize achievement system."""
        
        self.achievements = {}
        self._create_achievements()
        
        # Callbacks
        self.on_achievement_unlock = None
        
        print("[ACHIEVE] ✅ Achievement System initialized")
    
    def _create_achievements(self):
        """Create all achievements."""
        
        achievements_data = [
            ("first_block", "First Blood", "Block your first threat", "🎯"),
            ("block_10", "Defender", "Block 10 threats", "🛡️"),
            ("block_50", "Guardian", "Block 50 threats", "⚔️"),
            ("block_100", "Protector", "Block 100 threats", "🏰"),
            ("combo_5", "Combo Starter", "Get a 5x combo", "⚡"),
            ("combo_10", "Combo Master", "Get a 10x combo", "💫"),
            ("combo_20", "Combo Legend", "Get a 20x combo", "🌟"),
            ("wave_1", "Survivor", "Complete Wave 1", "🌊"),
            ("wave_5", "Veteran", "Complete Wave 5", "🎖️"),
            ("wave_10", "Champion", "Complete Wave 10", "👑"),
            ("no_damage", "Untouchable", "Complete a wave without damage", "💎"),
            ("score_1000", "Scorer", "Reach 1000 points", "📊"),
            ("score_5000", "High Scorer", "Reach 5000 points", "📈"),
            ("score_10000", "Score Master", "Reach 10000 points", "🏆"),
            ("auto_defense", "Automation", "Use auto-defense mode", "🤖"),
            ("critical_save", "Close Call", "Survive critical threat level", "😰"),
        ]
        
        for id, name, desc, icon in achievements_data:
            self.achievements[id] = Achievement(id, name, desc, icon)
    
    def check_and_unlock(self, achievement_id: str) -> bool:
        """Check and unlock an achievement."""
        
        if achievement_id in self.achievements:
            achievement = self.achievements[achievement_id]
            
            if achievement.unlock():
                if self.on_achievement_unlock:
                    self.on_achievement_unlock(achievement)
                return True
        
        return False
    
    def check_block_achievements(self, total_blocked: int):
        """Check block-related achievements."""
        
        if total_blocked >= 1:
            self.check_and_unlock("first_block")
        if total_blocked >= 10:
            self.check_and_unlock("block_10")
        if total_blocked >= 50:
            self.check_and_unlock("block_50")
        if total_blocked >= 100:
            self.check_and_unlock("block_100")
    
    def check_combo_achievements(self, combo: int):
        """Check combo-related achievements."""
        
        if combo >= 5:
            self.check_and_unlock("combo_5")
        if combo >= 10:
            self.check_and_unlock("combo_10")
        if combo >= 20:
            self.check_and_unlock("combo_20")
    
    def check_wave_achievements(self, wave: int):
        """Check wave-related achievements."""
        
        if wave >= 1:
            self.check_and_unlock("wave_1")
        if wave >= 5:
            self.check_and_unlock("wave_5")
        if wave >= 10:
            self.check_and_unlock("wave_10")
    
    def check_score_achievements(self, score: int):
        """Check score-related achievements."""
        
        if score >= 1000:
            self.check_and_unlock("score_1000")
        if score >= 5000:
            self.check_and_unlock("score_5000")
        if score >= 10000:
            self.check_and_unlock("score_10000")
    
    def get_unlocked(self) -> List[Achievement]:
        """Get all unlocked achievements."""
        
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked(self) -> List[Achievement]:
        """Get all locked achievements."""
        
        return [a for a in self.achievements.values() if not a.unlocked]
    
    def get_progress(self) -> Dict:
        """Get achievement progress."""
        
        total = len(self.achievements)
        unlocked = len(self.get_unlocked())
        
        return {
            'total': total,
            'unlocked': unlocked,
            'locked': total - unlocked,
            'percentage': int((unlocked / total) * 100) if total > 0 else 0
        }
    
    def reset(self):
        """Reset all achievements."""
        
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_time = None


# ============================================
# END GAME REPORT
# ============================================

class EndGameReport:
    """
    Generates end-game statistics report.
    """
    
    def __init__(self):
        """Initialize end game report."""
        
        self.report_data = {}
    
    def generate(self, game_stats: Dict, score_stats: Dict, 
                 wave_stats: Dict, achievements: List) -> Dict:
        """Generate comprehensive end-game report."""
        
        self.report_data = {
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S"),
            'game_time': game_stats.get('game_time', 0),
            'game_time_formatted': self._format_time(game_stats.get('game_time', 0)),
            
            # Health
            'final_health': game_stats.get('health', 0),
            'survived': game_stats.get('health', 0) > 0,
            
            # Score
            'final_score': score_stats.get('score', 0),
            'high_score': score_stats.get('high_score', 0),
            'is_new_high_score': score_stats.get('score', 0) >= score_stats.get('high_score', 0),
            
            # Combos
            'max_combo': score_stats.get('max_combo', 0),
            'best_multiplier': score_stats.get('multiplier', 1),
            
            # Blocking
            'total_blocked': score_stats.get('total_blocked', 0),
            'malicious_blocked': score_stats.get('malicious_blocked', 0),
            'suspicious_blocked': score_stats.get('suspicious_blocked', 0),
            'packets_processed': game_stats.get('packets_processed', 0),
            
            # Waves
            'waves_completed': wave_stats.get('waves_completed', 0),
            'highest_wave': wave_stats.get('current_wave', 0),
            
            # Achievements
            'achievements_unlocked': len(achievements),
            'achievements': [{'name': a.name, 'icon': a.icon} for a in achievements],
            
            # Grade
            'grade': self._calculate_grade(score_stats, wave_stats, game_stats)
        }
        
        return self.report_data
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS."""
        
        minutes = int(seconds) // 60
        secs = int(seconds) % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def _calculate_grade(self, score_stats: Dict, wave_stats: Dict, game_stats: Dict) -> str:
        """Calculate player grade based on performance."""
        
        score = score_stats.get('score', 0)
        waves = wave_stats.get('waves_completed', 0)
        health = game_stats.get('health', 0)
        
        # Calculate grade points
        points = 0
        points += min(score // 500, 30)  # Max 30 points from score
        points += waves * 5  # 5 points per wave
        points += health // 5  # Points from remaining health
        points += score_stats.get('max_combo', 0)  # Bonus from combo
        
        # Determine grade
        if points >= 80:
            return 'S'
        elif points >= 60:
            return 'A'
        elif points >= 45:
            return 'B'
        elif points >= 30:
            return 'C'
        elif points >= 15:
            return 'D'
        else:
            return 'F'
    
    def print_report(self):
        """Print report to console."""
        
        data = self.report_data
        
        print("\n" + "=" * 50)
        print("       CYBER DEFENSE - MISSION REPORT")
        print("=" * 50)
        
        print(f"\n  Result: {'MISSION COMPLETE' if data.get('survived') else 'MISSION FAILED'}")
        print(f"  Grade: {data.get('grade', 'N/A')}")
        print(f"  Time: {data.get('game_time_formatted', '00:00')}")
        
        print(f"\n  SCORE")
        print(f"  Final Score: {data.get('final_score', 0)}")
        if data.get('is_new_high_score'):
            print(f"  ★ NEW HIGH SCORE! ★")
        print(f"  Max Combo: {data.get('max_combo', 0)}x")
        
        print(f"\n  DEFENSE")
        print(f"  Threats Blocked: {data.get('total_blocked', 0)}")
        print(f"  Malicious: {data.get('malicious_blocked', 0)}")
        print(f"  Suspicious: {data.get('suspicious_blocked', 0)}")
        
        print(f"\n  PROGRESS")
        print(f"  Waves Completed: {data.get('waves_completed', 0)}")
        print(f"  Final Health: {data.get('final_health', 0)}%")
        
        if data.get('achievements'):
            print(f"\n  ACHIEVEMENTS ({data.get('achievements_unlocked', 0)})")
            for a in data.get('achievements', []):
                print(f"  {a['icon']} {a['name']}")
        
        print("\n" + "=" * 50)


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("Testing Game Enhancement Systems...")
    
    # Test Wave System
    print("\n[TEST] Wave System")
    waves = WaveSystem()
    waves.start_game()
    print(f"  Current wave: {waves.current_wave}")
    print(f"  Spawn rate: {waves.get_spawn_rate()}")
    
    # Test Score System
    print("\n[TEST] Score System")
    score = ScoreSystem()
    points = score.add_block_score('malicious')
    print(f"  Points earned: {points}")
    print(f"  Total score: {score.score}")
    print(f"  Combo: {score.combo}")
    
    # Test Achievement System
    print("\n[TEST] Achievement System")
    achievements = AchievementSystem()
    achievements.check_and_unlock("first_block")
    unlocked = achievements.get_unlocked()
    print(f"  Unlocked: {len(unlocked)}")
    
    print("\nAll tests passed!")
