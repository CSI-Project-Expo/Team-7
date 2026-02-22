"""
===========================================================
FILE: advanced_features.py
PURPOSE: Advanced innovative features for cyber defense game
FEATURES: World Map, Boss Battles, Live Graph, Power-ups
===========================================================
"""

import pygame
import random
import math
import time
from typing import Dict, List, Tuple

print("[ADVANCED] Loading advanced features...")


# ============================================
# COUNTRY DATA FOR WORLD MAP
# ============================================

COUNTRIES = {
    'Russia': {'pos': (0.65, 0.25), 'color': (255, 50, 50), 'threat': 0.8},
    'China': {'pos': (0.75, 0.40), 'color': (255, 100, 50), 'threat': 0.7},
    'USA': {'pos': (0.20, 0.35), 'color': (50, 150, 255), 'threat': 0.3},
    'Brazil': {'pos': (0.30, 0.65), 'color': (50, 255, 50), 'threat': 0.4},
    'India': {'pos': (0.68, 0.45), 'color': (255, 150, 50), 'threat': 0.5},
    'Germany': {'pos': (0.52, 0.30), 'color': (255, 200, 50), 'threat': 0.3},
    'Nigeria': {'pos': (0.50, 0.55), 'color': (200, 50, 200), 'threat': 0.6},
    'Iran': {'pos': (0.60, 0.40), 'color': (255, 80, 80), 'threat': 0.7},
    'N.Korea': {'pos': (0.80, 0.35), 'color': (255, 30, 30), 'threat': 0.9},
    'Unknown': {'pos': (0.50, 0.50), 'color': (150, 150, 150), 'threat': 0.5},
}


# ============================================
# MINI WORLD MAP
# ============================================

class MiniWorldMap:
    """
    Shows attack origins on a mini world map.
    Very impressive for judges!
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.attacks = []  # List of (country, timestamp)
        self.max_attacks = 20
        self.pulse_phase = 0
        
        print("[MAP] ✅ World Map initialized")
    
    def add_attack(self, country: str = None):
        """Register an attack from a country."""
        if country is None:
            # Random country weighted by threat level
            countries = list(COUNTRIES.keys())
            weights = [COUNTRIES[c]['threat'] for c in countries]
            country = random.choices(countries, weights=weights)[0]
        
        self.attacks.append({
            'country': country,
            'time': time.time(),
            'pulse': 0
        })
        
        # Limit attacks
        if len(self.attacks) > self.max_attacks:
            self.attacks.pop(0)
        
        return country
    
    def update(self):
        """Update animations."""
        self.pulse_phase += 0.1
        
        # Update attack pulses
        for attack in self.attacks:
            attack['pulse'] += 0.15
        
        # Remove old attacks (older than 10 seconds)
        current_time = time.time()
        self.attacks = [a for a in self.attacks if current_time - a['time'] < 10]
    
    def draw(self, surface):
        """Draw the mini world map."""
        # Background
        pygame.draw.rect(surface, (15, 25, 40), self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 200, 255), self.rect, 2, border_radius=5)
        
        # Title
        font = pygame.font.Font(None, 18)
        title = font.render("ATTACK ORIGINS", True, (0, 200, 255))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Draw simplified world map (continents as shapes)
        map_rect = pygame.Rect(
            self.rect.x + 5,
            self.rect.y + 25,
            self.rect.width - 10,
            self.rect.height - 30
        )
        
        # Draw continent outlines (simplified)
        pygame.draw.rect(surface, (30, 50, 70), map_rect, border_radius=3)
        
        # Draw countries as dots
        for country, data in COUNTRIES.items():
            x = map_rect.x + int(data['pos'][0] * map_rect.width)
            y = map_rect.y + int(data['pos'][1] * map_rect.height)
            
            # Small dot for country
            pygame.draw.circle(surface, (50, 80, 100), (x, y), 3)
        
        # Draw active attacks with pulse effect
        for attack in self.attacks:
            country = attack['country']
            if country in COUNTRIES:
                data = COUNTRIES[country]
                x = map_rect.x + int(data['pos'][0] * map_rect.width)
                y = map_rect.y + int(data['pos'][1] * map_rect.height)
                
                # Pulse effect
                pulse_size = 5 + abs(math.sin(attack['pulse'])) * 8
                alpha = int(200 - attack['pulse'] * 10)
                alpha = max(50, min(255, alpha))
                
                # Draw pulse ring
                pulse_surface = pygame.Surface((int(pulse_size * 3), int(pulse_size * 3)), pygame.SRCALPHA)
                pygame.draw.circle(
                    pulse_surface,
                    (*data['color'], alpha),
                    (int(pulse_size * 1.5), int(pulse_size * 1.5)),
                    int(pulse_size)
                )
                surface.blit(pulse_surface, (x - pulse_size * 1.5, y - pulse_size * 1.5))
                
                # Center dot
                pygame.draw.circle(surface, data['color'], (x, y), 4)
        
        # Draw attack count by country
        country_counts = {}
        for attack in self.attacks:
            c = attack['country']
            country_counts[c] = country_counts.get(c, 0) + 1
        
        # Show top attacker
        if country_counts:
            top_country = max(country_counts, key=country_counts.get)
            count = country_counts[top_country]
            
            info_font = pygame.font.Font(None, 16)
            info = info_font.render(f"Top: {top_country} ({count})", True, (255, 100, 100))
            surface.blit(info, (self.rect.x + 5, self.rect.y + self.rect.height - 18))
    
    def get_top_attacker(self) -> str:
        """Get country with most attacks."""
        country_counts = {}
        for attack in self.attacks:
            c = attack['country']
            country_counts[c] = country_counts.get(c, 0) + 1
        
        if country_counts:
            return max(country_counts, key=country_counts.get)
        return "Unknown"


# ============================================
# LIVE THREAT GRAPH
# ============================================

class LiveThreatGraph:
    """
    Real-time line graph showing threat level over time.
    Professional dashboard look!
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.data_points = []
        self.max_points = 60  # 60 seconds of data
        self.max_value = 100
        
        print("[GRAPH] ✅ Live Graph initialized")
    
    def add_point(self, value: float):
        """Add a data point."""
        self.data_points.append({
            'value': min(self.max_value, max(0, value)),
            'time': time.time()
        })
        
        # Keep only recent points
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)
    
    def draw(self, surface):
        """Draw the graph."""
        # Background
        pygame.draw.rect(surface, (15, 25, 40), self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 255, 150), self.rect, 2, border_radius=5)
        
        # Title
        font = pygame.font.Font(None, 18)
        title = font.render("THREAT LEVEL", True, (0, 255, 150))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Graph area
        graph_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 25,
            self.rect.width - 20,
            self.rect.height - 35
        )
        
        # Draw grid lines
        for i in range(5):
            y = graph_rect.y + (i * graph_rect.height // 4)
            pygame.draw.line(surface, (30, 50, 70), (graph_rect.x, y), (graph_rect.right, y), 1)
        
        # Draw data line
        if len(self.data_points) > 1:
            points = []
            for i, dp in enumerate(self.data_points):
                x = graph_rect.x + (i * graph_rect.width // max(1, len(self.data_points) - 1))
                y = graph_rect.bottom - (dp['value'] / self.max_value * graph_rect.height)
                points.append((x, int(y)))
            
            if len(points) > 1:
                # Determine color based on last value
                last_value = self.data_points[-1]['value']
                if last_value > 70:
                    line_color = (255, 50, 50)
                elif last_value > 40:
                    line_color = (255, 200, 50)
                else:
                    line_color = (50, 255, 150)
                
                pygame.draw.lines(surface, line_color, False, points, 2)
                
                # Draw current value dot
                pygame.draw.circle(surface, line_color, points[-1], 4)
        
        # Draw current value
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
        self.attack_interval = 60  # frames
        self.defeated = False
        
        # Boss types
        self.boss_data = {
            'DDOS_LORD': {
                'name': 'DDoS Lord',
                'color': (255, 50, 50),
                'size': 40,
                'attack': 'flood',
                'description': 'Floods with massive packets'
            },
            'MALWARE_KING': {
                'name': 'Malware King',
                'color': (150, 0, 200),
                'size': 45,
                'attack': 'infect',
                'description': 'Infects packets'
            },
            'RANSOM_MASTER': {
                'name': 'Ransomware Master',
                'color': (255, 150, 0),
                'size': 42,
                'attack': 'encrypt',
                'description': 'Encrypts your defenses'
            },
            'PHISH_EMPEROR': {
                'name': 'Phishing Emperor',
                'color': (0, 200, 255),
                'size': 38,
                'attack': 'deceive',
                'description': 'Disguises attacks as safe'
            },
            'BOTNET_QUEEN': {
                'name': 'Botnet Queen',
                'color': (255, 50, 200),
                'size': 44,
                'attack': 'swarm',
                'description': 'Commands bot army'
            }
        }
        
        self.data = self.boss_data.get(boss_type, self.boss_data['DDOS_LORD'])
        self.pulse = 0
    
    def update(self):
        """Update boss state."""
        self.pulse += 0.1
        self.attack_timer += 1
        
        # Move towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx*dx + dy*dy)
        
        if dist > 5:
            self.x += dx * 0.02
            self.y += dy * 0.02
        
        # Check if should attack
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
        
        # Pulse effect
        pulse_size = size + abs(math.sin(self.pulse)) * 10
        
        # Draw outer glow
        for i in range(3):
            glow_size = pulse_size + i * 8
            glow_alpha = 100 - i * 30
            glow_surface = pygame.Surface((int(glow_size * 2.5), int(glow_size * 2.5)), pygame.SRCALPHA)
            pygame.draw.circle(
                glow_surface,
                (*color, glow_alpha),
                (int(glow_size * 1.25), int(glow_size * 1.25)),
                int(glow_size)
            )
            surface.blit(glow_surface, (self.x - glow_size * 1.25, self.y - glow_size * 1.25))
        
        # Draw boss body
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(size))
        
        # Draw angry eyes
        eye_offset = size // 3
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - eye_offset), int(self.y - 5)), 8)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + eye_offset), int(self.y - 5)), 8)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x - eye_offset), int(self.y - 5)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + eye_offset), int(self.y - 5)), 4)
        
        # Draw evil mouth
        mouth_points = [
            (int(self.x - 15), int(self.y + 10)),
            (int(self.x), int(self.y + 20)),
            (int(self.x + 15), int(self.y + 10))
        ]
        pygame.draw.lines(surface, (0, 0, 0), False, mouth_points, 3)
        
        # Draw health bar
        bar_width = 60
        bar_height = 8
        bar_x = self.x - bar_width // 2
        bar_y = self.y - size - 20
        
        # Background
        pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = (255, 50, 50) if self.health < self.max_health * 0.3 else (255, 200, 50) if self.health < self.max_health * 0.6 else (50, 255, 50)
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(surface, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1)
        
        # Boss name
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
        """Check if boss is active."""
        return self.current_boss is not None and self.current_boss.active
    
    def get_boss(self) -> Boss:
        """Get current boss."""
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
        self.lifetime = 600  # 10 seconds at 60fps
        
        self.power_data = {
            'shield': {
                'name': 'Shield',
                'color': (0, 200, 255),
                'icon': 'S',
                'duration': 300,
                'description': 'Blocks all damage'
            },
            'rapid_fire': {
                'name': 'Rapid Block',
                'color': (255, 200, 0),
                'icon': 'R',
                'duration': 300,
                'description': 'Auto-block faster'
            },
            'heal': {
                'name': 'Heal',
                'color': (0, 255, 100),
                'icon': '+',
                'duration': 0,
                'description': '+25 Health'
            },
            'nuke': {
                'name': 'Nuke',
                'color': (255, 50, 50),
                'icon': 'N',
                'duration': 0,
                'description': 'Clear all threats'
            },
            'double_score': {
                'name': '2X Score',
                'color': (255, 0, 255),
                'icon': '2X',
                'duration': 600,
                'description': 'Double points'
            }
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
        
        # Floating animation
        float_offset = math.sin(self.pulse) * 5
        draw_y = self.y + float_offset
        
        # Glow effect
        glow_size = self.size + abs(math.sin(self.pulse * 2)) * 8
        glow_surface = pygame.Surface((int(glow_size * 3), int(glow_size * 3)), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surface,
            (*color, 80),
            (int(glow_size * 1.5), int(glow_size * 1.5)),
            int(glow_size)
        )
        surface.blit(glow_surface, (self.x - glow_size * 1.5, draw_y - glow_size * 1.5))
        
        # Main circle
        pygame.draw.circle(surface, color, (int(self.x), int(draw_y)), self.size)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(draw_y)), self.size, 2)
        
        # Icon
        font = pygame.font.Font(None, 24)
        icon = font.render(self.data['icon'], True, (255, 255, 255))
        icon_rect = icon.get_rect(center=(self.x, draw_y))
        surface.blit(icon, icon_rect)
    
    def contains_point(self, point) -> bool:
        """Check if point is inside power-up."""
        px, py = point
        dist = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
        return dist <= self.size + 10


class PowerUpSystem:
    """Manages power-ups."""
    
    def __init__(self):
        self.power_ups = []
        self.active_effects = {}  # {power_type: end_time}
        self.spawn_timer = 0
        self.spawn_interval = 600  # Every 10 seconds
        
        self.on_powerup_collect = None
        
        print("[POWERUP] ✅ Power-up System initialized")
    
    def update(self, game_area_x, game_area_y, game_area_width, game_area_height):
        """Update power-ups."""
        self.spawn_timer += 1
        
        # Spawn new power-up
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            
            # Random position in game area
            x = game_area_x + random.randint(100, game_area_width - 100)
            y = game_area_y + random.randint(100, game_area_height - 100)
            
            # Random type
            power_type = random.choice(['shield', 'rapid_fire', 'heal', 'nuke', 'double_score'])
            
            self.power_ups.append(PowerUp(x, y, power_type))
        
        # Update existing power-ups
        self.power_ups = [p for p in self.power_ups if p.update()]
        
        # Update active effects
        current_time = time.time()
        expired = [k for k, v in self.active_effects.items() if current_time > v]
        for k in expired:
            del self.active_effects[k]
    
    def check_collection(self, point) -> PowerUp:
        """Check if point collects a power-up."""
        for power_up in self.power_ups:
            if power_up.active and power_up.contains_point(point):
                power_up.active = False
                
                # Apply effect
                duration = power_up.data['duration'] / 60  # Convert frames to seconds
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
        """Check if effect is active."""
        return power_type in self.active_effects
    
    def get_active_effects(self) -> List[str]:
        """Get list of active effects."""
        return list(self.active_effects.keys())
    
    def clear(self):
        """Clear all power-ups."""
        self.power_ups.clear()


# ============================================
# ATTACK DNA VISUALIZATION
# ============================================

class AttackDNA:
    """
    Visual representation of attack patterns.
    Looks like DNA helix - very unique!
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.pattern = []  # List of attack types
        self.max_pattern = 30
        self.phase = 0
        
        print("[DNA] ✅ Attack DNA initialized")
    
    def add_attack(self, attack_type: str):
        """Add attack to pattern."""
        type_colors = {
            'safe': (0, 200, 255),
            'suspicious': (255, 200, 0),
            'malicious': (255, 50, 50),
            'blocked': (100, 100, 100)
        }
        
        color = type_colors.get(attack_type, (150, 150, 150))
        self.pattern.append({'type': attack_type, 'color': color})
        
        if len(self.pattern) > self.max_pattern:
            self.pattern.pop(0)
    
    def update(self):
        """Update animation."""
        self.phase += 0.05
    
    def draw(self, surface):
        """Draw DNA helix."""
        # Background
        pygame.draw.rect(surface, (15, 25, 40), self.rect, border_radius=5)
        pygame.draw.rect(surface, (200, 50, 200), self.rect, 2, border_radius=5)
        
        # Title
        font = pygame.font.Font(None, 18)
        title = font.render("ATTACK DNA", True, (200, 50, 200))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        if len(self.pattern) < 2:
            return
        
        # Draw DNA helix
        helix_rect = pygame.Rect(
            self.rect.x + 10,
            self.rect.y + 25,
            self.rect.width - 20,
            self.rect.height - 35
        )
        
        center_y = helix_rect.centery
        amplitude = helix_rect.height // 3
        
        for i, attack in enumerate(self.pattern):
            x = helix_rect.x + (i * helix_rect.width // max(1, len(self.pattern) - 1))
            
            # Two strands of DNA
            phase_offset = self.phase + i * 0.3
            
            y1 = center_y + math.sin(phase_offset) * amplitude
            y2 = center_y + math.sin(phase_offset + math.pi) * amplitude
            
            # Draw connecting line
            pygame.draw.line(surface, (50, 50, 80), (x, int(y1)), (x, int(y2)), 1)
            
            # Draw nodes
            pygame.draw.circle(surface, attack['color'], (int(x), int(y1)), 4)
            pygame.draw.circle(surface, attack['color'], (int(x), int(y2)), 4)


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\nTesting Advanced Features...")
    
    print("\n[TEST] World Map")
    world_map = MiniWorldMap(0, 0, 200, 150)
    world_map.add_attack("Russia")
    world_map.add_attack("China")
    print(f"  Top attacker: {world_map.get_top_attacker()}")
    
    print("\n[TEST] Live Graph")
    graph = LiveThreatGraph(0, 0, 200, 100)
    graph.add_point(25)
    graph.add_point(50)
    graph.add_point(75)
    print(f"  Data points: {len(graph.data_points)}")
    
    print("\n[TEST] Boss System")
    boss_system = BossSystem()
    boss = boss_system.spawn_boss(5, 100, 100, 300, 200)
    print(f"  Boss: {boss.data['name']}")
    print(f"  Health: {boss.health}")
    
    print("\n[TEST] Power-up System")
    powerup_system = PowerUpSystem()
    print(f"  Active power-ups: {len(powerup_system.power_ups)}")
    
    print("\n[TEST] Attack DNA")
    dna = AttackDNA(0, 0, 200, 100)
    dna.add_attack('malicious')
    dna.add_attack('safe')
    dna.add_attack('suspicious')
    print(f"  Pattern length: {len(dna.pattern)}")
    
    print("\n✅ All advanced features working!")
