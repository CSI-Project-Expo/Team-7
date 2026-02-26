"""
===========================================================
FILE: advanced_features.py
PURPOSE: Boss Battles, Power-ups, Live Graph
===========================================================
"""

import pygame
import random
import math
import time
from typing import Dict, List

print("[ADVANCED] Loading advanced features...")


# ============================================
# LIVE THREAT GRAPH
# ============================================

class LiveThreatGraph:
    """Real-time line graph showing threat level over time."""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.data_points = []
        self.max_points = 60
        self.max_value = 100
        
        print("[GRAPH] ✅ Live Graph initialized")
    
    def add_point(self, value: float):
        """Add a data point."""
        self.data_points.append({
            'value': min(self.max_value, max(0, value)),
            'time': time.time()
        })
        
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
    
    def draw(self, surface):
        """Draw the graph."""
        pygame.draw.rect(surface, (15, 25, 40), self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 255, 150), self.rect, 2, border_radius=5)
        
        font = pygame.font.Font(None, 18)
        title = font.render("THREAT LEVEL", True, (0, 255, 150))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        graph_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 25,
            self.rect.width - 20,
            self.rect.height - 35
        )
        
        for i in range(5):
            y = graph_rect.y + (i * graph_rect.height // 4)
            pygame.draw.line(surface, (30, 50, 70), (graph_rect.x, y), (graph_rect.right, y), 1)
        
        if len(self.data_points) > 1:
            points = []
            for i, dp in enumerate(self.data_points):
                x = graph_rect.x + (i * graph_rect.width // max(1, len(self.data_points) - 1))
                y = graph_rect.bottom - (dp['value'] / self.max_value * graph_rect.height)
                points.append((x, int(y)))
            
            if len(points) > 1:
                last_value = self.data_points[-1]['value']
                if last_value > 70:
                    line_color = (255, 50, 50)
                elif last_value > 40:
                    line_color = (255, 200, 50)
                else:
                    line_color = (50, 255, 150)
                
                pygame.draw.lines(surface, line_color, False, points, 2)
                pygame.draw.circle(surface, line_color, points[-1], 4)
        
        if self.data_points:
            value = int(self.data_points[-1]['value'])
            value_font = pygame.font.Font(None, 20)
            value_text = value_font.render(f"{value}%", True, (255, 255, 255))
            surface.blit(value_text, (self.rect.right - 35, self.rect.y + 5))


# ============================================
# BOSS BATTLE SYSTEM
# ============================================

class Boss:
    """A boss enemy with special attacks."""
    
    def __init__(self, boss_type: str, wave: int):
        self.boss_type = boss_type
        self.wave = wave
        self.health = 100 + (wave * 20)
        self.max_health = self.health
        self.x = 0
        self.y = 0
        self.target_x = 0
        self.target_y = 0
        self.active = True
        self.attack_timer = 0
        self.attack_interval = 60
        self.defeated = False
        
        self.boss_data = {
            'DDOS_LORD': {'name': 'DDoS Lord', 'color': (255, 50, 50), 'size': 40},
            'MALWARE_KING': {'name': 'Malware King', 'color': (150, 0, 200), 'size': 45},
            'RANSOM_MASTER': {'name': 'Ransomware Master', 'color': (255, 150, 0), 'size': 42},
            'PHISH_EMPEROR': {'name': 'Phishing Emperor', 'color': (0, 200, 255), 'size': 38},
            'BOTNET_QUEEN': {'name': 'Botnet Queen', 'color': (255, 50, 200), 'size': 44}
        }
        
        self.data = self.boss_data.get(boss_type, self.boss_data['DDOS_LORD'])
        self.pulse = 0
    
    def update(self):
        """Update boss state."""
        self.pulse += 0.1
        self.attack_timer += 1
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 5:
            self.x += dx * 0.02
            self.y += dy * 0.02
        
        should_attack = self.attack_timer >= self.attack_interval
        if should_attack:
            self.attack_timer = 0
        
        return should_attack
    
    def take_damage(self, amount: int):
        """Boss takes damage."""
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.defeated = True
            self.active = False
        return self.defeated
    
    def draw(self, surface):
        """Draw the boss."""
        if not self.active:
            return
        
        size = self.data['size']
        color = self.data['color']
        
        pulse_size = size + abs(math.sin(self.pulse)) * 10
        
        for i in range(3):
            glow_size = pulse_size + i * 8
            glow_alpha = 100 - i * 30
            glow_surface = pygame.Surface((int(glow_size * 2.5), int(glow_size * 2.5)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*color, glow_alpha), (int(glow_size * 1.25), int(glow_size * 1.25)), int(glow_size))
            surface.blit(glow_surface, (self.x - glow_size * 1.25, self.y - glow_size * 1.25))
        
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(size))
        
        eye_offset = size // 3
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - eye_offset), int(self.y - 5)), 8)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + eye_offset), int(self.y - 5)), 8)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x - eye_offset), int(self.y - 5)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + eye_offset), int(self.y - 5)), 4)
        
        mouth_points = [(int(self.x - 15), int(self.y + 10)), (int(self.x), int(self.y + 20)), (int(self.x + 15), int(self.y + 10))]
        pygame.draw.lines(surface, (0, 0, 0), False, mouth_points, 3)
        
        bar_width = 60
        bar_height = 8
        bar_x = self.x - bar_width // 2
        bar_y = self.y - size - 20
        
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = (255, 50, 50) if self.health < self.max_health * 0.3 else (255, 200, 50) if self.health < self.max_health * 0.6 else (50, 255, 50)
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        font = pygame.font.Font(None, 20)
        name = font.render(self.data['name'], True, (255, 255, 255))
        name_rect = name.get_rect(center=(self.x, bar_y - 12))
        surface.blit(name, name_rect)


class BossSystem:
    """Manages boss battles."""
    
    def __init__(self):
        self.current_boss = None
        self.bosses_defeated = 0
        self.boss_types = ['DDOS_LORD', 'MALWARE_KING', 'RANSOM_MASTER', 'PHISH_EMPEROR', 'BOTNET_QUEEN']
        
        self.on_boss_spawn = None
        self.on_boss_attack = None
        self.on_boss_defeated = None
        
        print("[BOSS] ✅ Boss System initialized")
    
    def spawn_boss(self, wave: int, x: float, y: float, target_x: float, target_y: float):
        """Spawn a boss for the wave."""
        boss_type = self.boss_types[(wave // 5 - 1) % len(self.boss_types)]
        
        self.current_boss = Boss(boss_type, wave)
        self.current_boss.x = x
        self.current_boss.y = y
        self.current_boss.target_x = target_x
        self.current_boss.target_y = target_y
        
        if self.on_boss_spawn:
            self.on_boss_spawn(self.current_boss)
        
        return self.current_boss
    
    def update(self):
        """Update boss system."""
        if self.current_boss and self.current_boss.active:
            should_attack = self.current_boss.update()
            
            if should_attack and self.on_boss_attack:
                self.on_boss_attack(self.current_boss)
            
            return True
        return False
    
    def damage_boss(self, amount: int):
        """Damage the current boss."""
        if self.current_boss and self.current_boss.active:
            defeated = self.current_boss.take_damage(amount)
            
            if defeated:
                self.bosses_defeated += 1
                if self.on_boss_defeated:
                    self.on_boss_defeated(self.current_boss)
                self.current_boss = None
                return True
        return False
    
    def draw(self, surface):
        """Draw the boss."""
        if self.current_boss and self.current_boss.active:
            self.current_boss.draw(surface)
    
    def has_boss(self) -> bool:
        return self.current_boss is not None and self.current_boss.active
    
    def get_boss(self) -> Boss:
        return self.current_boss


# ============================================
# POWER-UP SYSTEM
# ============================================

class PowerUp:
    """A collectible power-up."""
    
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.active = True
        self.pulse = random.uniform(0, math.pi * 2)
        self.lifetime = 600
        
        self.power_data = {
            'shield': {'name': 'Shield', 'color': (0, 200, 255), 'icon': 'S', 'duration': 300},
            'rapid_fire': {'name': 'Rapid Block', 'color': (255, 200, 0), 'icon': 'R', 'duration': 300},
            'heal': {'name': 'Heal', 'color': (0, 255, 100), 'icon': '+', 'duration': 0},
            'nuke': {'name': 'Nuke', 'color': (255, 50, 50), 'icon': 'N', 'duration': 0},
            'double_score': {'name': '2X Score', 'color': (255, 0, 255), 'icon': '2X', 'duration': 600}
        }
        
        self.data = self.power_data.get(power_type, self.power_data['shield'])
        self.size = 20
    
    def update(self):
        """Update power-up."""
        self.pulse += 0.1
        self.lifetime -= 1
        
        if self.lifetime <= 0:
            self.active = False
        
        return self.active
    
    def draw(self, surface):
        """Draw power-up."""
        if not self.active:
            return
        
        color = self.data['color']
        
        float_offset = math.sin(self.pulse) * 5
        draw_y = self.y + float_offset
        
        glow_size = self.size + abs(math.sin(self.pulse * 2)) * 8
        glow_surface = pygame.Surface((int(glow_size * 3), int(glow_size * 3)), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*color, 80), (int(glow_size * 1.5), int(glow_size * 1.5)), int(glow_size))
        surface.blit(glow_surface, (self.x - glow_size * 1.5, draw_y - glow_size * 1.5))
        
        pygame.draw.circle(surface, color, (int(self.x), int(draw_y)), self.size)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(draw_y)), self.size, 2)
        
        font = pygame.font.Font(None, 24)
        icon = font.render(self.data['icon'], True, (255, 255, 255))
        icon_rect = icon.get_rect(center=(self.x, draw_y))
        surface.blit(icon, icon_rect)
    
    def contains_point(self, point) -> bool:
        px, py = point
        dist = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return dist <= self.size + 10


class PowerUpSystem:
    """Manages power-ups."""
    
    def __init__(self):
        self.power_ups = []
        self.active_effects = {}
        self.spawn_timer = 0
        self.spawn_interval = 600
        
        self.on_powerup_collect = None
        
        print("[POWERUP] ✅ Power-up System initialized")
    
    def update(self, game_area_x, game_area_y, game_area_width, game_area_height):
        """Update power-ups."""
        self.spawn_timer += 1
        
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            
            x = game_area_x + random.randint(100, game_area_width - 100)
            y = game_area_y + random.randint(100, game_area_height - 100)
            
            power_type = random.choice(['shield', 'rapid_fire', 'heal', 'nuke', 'double_score'])
            
            self.power_ups.append(PowerUp(x, y, power_type))
        
        self.power_ups = [p for p in self.power_ups if p.update()]
        
        current_time = time.time()
        expired = [k for k, v in self.active_effects.items() if current_time > v]
        for k in expired:
            del self.active_effects[k]
    
    def check_collection(self, point) -> PowerUp:
        """Check if point collects a power-up."""
        for power_up in self.power_ups:
            if power_up.active and power_up.contains_point(point):
                power_up.active = False
                
                duration = power_up.data['duration'] / 60
                if duration > 0:
                    self.active_effects[power_up.power_type] = time.time() + duration
                
                if self.on_powerup_collect:
                    self.on_powerup_collect(power_up)
                
                return power_up
        
        return None
    
    def draw(self, surface):
        """Draw all power-ups."""
        for power_up in self.power_ups:
            power_up.draw(surface)
    
    def has_effect(self, power_type: str) -> bool:
        return power_type in self.active_effects
    
    def get_active_effects(self) -> List[str]:
        return list(self.active_effects.keys())
    
    def clear(self):
        self.power_ups.clear()


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\nTesting Advanced Features...")
    
    print("\n[TEST] Live Graph")
    graph = LiveThreatGraph(0, 0, 200, 100)
    graph.add_point(50)
    print(f"  Data points: {len(graph.data_points)}")
    
    print("\n[TEST] Boss System")
    boss_system = BossSystem()
    boss = boss_system.spawn_boss(5, 100, 100, 300, 200)
    print(f"  Boss: {boss.data['name']}")
    
    print("\n[TEST] Power-up System")
    powerup_system = PowerUpSystem()
    print(f"  Power-ups: {len(powerup_system.power_ups)}")
    
    print("\n✅ All features working!")
