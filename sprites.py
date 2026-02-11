

"""
sprites.py
Packet Sprite Classes for Cyber Defense Game

Author: Game UI Team
Description: Handles all moving packet objects on screen
"""

import pygame
import math
import random
from enum import Enum


# ============================================
# PACKET TYPES
# ============================================

class PacketType(Enum):
    """Different types of network packets"""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    MALICIOUS = "malicious"
    BLOCKED = "blocked"


# ============================================
# COLOR DEFINITIONS
# ============================================

class PacketColors:
    """Color scheme for packets"""
    SAFE = (0, 200, 255)           # Cyan blue
    SUSPICIOUS = (255, 200, 0)      # Yellow/Orange
    MALICIOUS = (255, 50, 80)       # Red
    BLOCKED = (100, 100, 100)       # Gray
    
    # Glow colors (slightly brighter)
    SAFE_GLOW = (100, 220, 255)
    SUSPICIOUS_GLOW = (255, 220, 100)
    MALICIOUS_GLOW = (255, 100, 120)
    
    @classmethod
    def get_color(cls, packet_type):
        """Get color based on packet type"""
        color_map = {
            PacketType.SAFE: cls.SAFE,
            PacketType.SUSPICIOUS: cls.SUSPICIOUS,
            PacketType.MALICIOUS: cls.MALICIOUS,
            PacketType.BLOCKED: cls.BLOCKED
        }
        return color_map.get(packet_type, cls.SAFE)
    
    @classmethod
    def get_glow_color(cls, packet_type):
        """Get glow color based on packet type"""
        glow_map = {
            PacketType.SAFE: cls.SAFE_GLOW,
            PacketType.SUSPICIOUS: cls.SUSPICIOUS_GLOW,
            PacketType.MALICIOUS: cls.MALICIOUS_GLOW,
            PacketType.BLOCKED: cls.BLOCKED
        }
        return glow_map.get(packet_type, cls.SAFE_GLOW)


# ============================================
# PACKET SPRITE CLASS
# ============================================

class PacketSprite(pygame.sprite.Sprite):
    """
    Represents a network packet moving across the screen.
    
    Features:
    - Smooth movement from source to target
    - Color based on threat level
    - Trail effect behind packet
    - Glow animation
    - Click detection for blocking
    """
    
    def __init__(self, start_x, start_y, target_x, target_y, 
                 packet_type=PacketType.SAFE, source_ip="0.0.0.0",
                 dest_ip="0.0.0.0", protocol="TCP"):
        """
        Initialize a packet sprite.
        
        Args:
            start_x: Starting X position
            start_y: Starting Y position
            target_x: Target X position
            target_y: Target Y position
            packet_type: Type of packet (SAFE, SUSPICIOUS, MALICIOUS, BLOCKED)
            source_ip: Source IP address (for display)
            dest_ip: Destination IP address (for display)
            protocol: Protocol type (TCP, UDP, etc.)
        """
        super().__init__()
        
        # ---- Position and Movement ----
        self.x = float(start_x)
        self.y = float(start_y)
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        
        # Speed varies slightly for visual interest
        self.speed = random.uniform(2.5, 4.5)
        
        # ---- Packet Information ----
        self.packet_type = packet_type
        self.source_ip = source_ip
        self.dest_ip = dest_ip
        self.protocol = protocol
        
        # ---- State Flags ----
        self.is_blocked = False
        self.reached_target = False
        self.is_selected = False
        
        # ---- Visual Properties ----
        self.radius = self._calculate_radius()
        self.color = PacketColors.get_color(packet_type)
        self.glow_color = PacketColors.get_glow_color(packet_type)
        
        # ---- Animation Properties ----
        self.glow_phase = random.uniform(0, math.pi * 2)
        self.glow_speed = 0.15
        self.trail_positions = []
        self.max_trail_length = 10
        self.alpha = 255
        self.fade_speed = 15
        
        # ---- Create Pygame Surface ----
        self._create_surface()
    
    def _calculate_radius(self):
        """Calculate sprite radius based on packet type"""
        try:
            if self.packet_type == PacketType.MALICIOUS:
                return 12
            elif self.packet_type == PacketType.SUSPICIOUS:
                return 10
            elif self.packet_type == PacketType.BLOCKED:
                return 8
            else:
                return 8
        except Exception:
            return 8
    
    def _create_surface(self):
        """Create the sprite surface with proper size"""
        try:
            size = self.radius * 4
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            self.rect.center = (int(self.x), int(self.y))
            self._draw_packet()
        except pygame.error as e:
            print(f"[ERROR] Failed to create packet surface: {e}")
            # Create minimal fallback surface
            self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
    
    def _draw_packet(self):
        """Draw the packet with glow effect"""
        try:
            self.image.fill((0, 0, 0, 0))  # Clear with transparency
            center = self.image.get_width() // 2
            
            # Calculate glow intensity (pulsing effect)
            glow_intensity = abs(math.sin(self.glow_phase)) * 0.5 + 0.5
            
            # Draw outer glow layers
            for i in range(4, 0, -1):
                glow_alpha = int(40 * glow_intensity / i)
                glow_radius = self.radius + i * 3
                
                glow_surface = pygame.Surface(
                    (glow_radius * 2, glow_radius * 2), 
                    pygame.SRCALPHA
                )
                glow_color = (*self.glow_color, glow_alpha)
                pygame.draw.circle(
                    glow_surface, 
                    glow_color, 
                    (glow_radius, glow_radius), 
                    glow_radius
                )
                
                pos = center - glow_radius
                self.image.blit(glow_surface, (pos, pos))
            
            # Draw main packet body
            pygame.draw.circle(self.image, self.color, (center, center), self.radius)
            
            # Draw inner highlight (gives 3D effect)
            highlight_color = tuple(min(c + 60, 255) for c in self.color)
            highlight_pos = (center - self.radius // 3, center - self.radius // 3)
            pygame.draw.circle(
                self.image, 
                highlight_color, 
                highlight_pos, 
                self.radius // 3
            )
            
            # Draw danger indicator for malicious packets
            if self.packet_type == PacketType.MALICIOUS:
                self._draw_danger_indicator(center)
            
            # Draw selection ring if selected
            if self.is_selected:
                pygame.draw.circle(
                    self.image, 
                    (255, 255, 255), 
                    (center, center), 
                    self.radius + 5, 
                    2
                )
                
        except Exception as e:
            print(f"[ERROR] Failed to draw packet: {e}")
    
    def _draw_danger_indicator(self, center):
        """Draw X mark for malicious packets"""
        try:
            offset = self.radius // 2
            line_color = (255, 255, 255)
            
            # Draw X
            pygame.draw.line(
                self.image, line_color,
                (center - offset, center - offset),
                (center + offset, center + offset), 2
            )
            pygame.draw.line(
                self.image, line_color,
                (center + offset, center - offset),
                (center - offset, center + offset), 2
            )
        except Exception:
            pass
    
    def update(self):
        """Update packet position and animation each frame"""
        try:
            # If blocked, fade out and stop
            if self.is_blocked:
                self._handle_blocked_state()
                return
            
            # If reached target, mark as complete
            if self.reached_target:
                return
            
            # Store current position for trail
            self._update_trail()
            
            # Calculate movement
            self._move_towards_target()
            
            # Update animation
            self.glow_phase += self.glow_speed
            
            # Update visual
            self._draw_packet()
            
            # Update rect position
            self.rect.center = (int(self.x), int(self.y))
            
        except Exception as e:
            print(f"[ERROR] Packet update failed: {e}")
    
    def _update_trail(self):
        """Store positions for trail effect"""
        self.trail_positions.append((int(self.x), int(self.y)))
        if len(self.trail_positions) > self.max_trail_length:
            self.trail_positions.pop(0)
    
    def _move_towards_target(self):
        """Move packet towards its target position"""
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.speed:
            # Reached target
            self.x = self.target_x
            self.y = self.target_y
            self.reached_target = True
        else:
            # Move towards target
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def _handle_blocked_state(self):
        """Handle fade out when blocked"""
        self.alpha -= self.fade_speed
        if self.alpha <= 0:
            self.kill()  # Remove from sprite group
        else:
            self.image.set_alpha(self.alpha)
    
    def draw_trail(self, surface):
        """Draw motion trail behind packet"""
        try:
            if len(self.trail_positions) < 2:
                return
            
            for i, pos in enumerate(self.trail_positions):
                # Calculate alpha based on position in trail
                alpha = int((i / len(self.trail_positions)) * 150)
                trail_radius = max(2, self.radius - 4)
                
                # Create trail dot surface
                trail_surface = pygame.Surface(
                    (trail_radius * 2, trail_radius * 2), 
                    pygame.SRCALPHA
                )
                trail_color = (*self.color, alpha)
                pygame.draw.circle(
                    trail_surface, 
                    trail_color, 
                    (trail_radius, trail_radius), 
                    trail_radius
                )
                
                surface.blit(
                    trail_surface, 
                    (pos[0] - trail_radius, pos[1] - trail_radius)
                )
        except Exception as e:
            print(f"[ERROR] Trail drawing failed: {e}")
    
    def block(self):
        """Mark packet as blocked"""
        self.is_blocked = True
        self.packet_type = PacketType.BLOCKED
        self.color = PacketColors.BLOCKED
        self._draw_packet()
    
    def select(self):
        """Toggle selection state"""
        self.is_selected = not self.is_selected
        self._draw_packet()
    
    def contains_point(self, point):
        """Check if a point is inside the packet (for click detection)"""
        try:
            px, py = point
            distance = math.sqrt((px - self.x) ** 2 + (py - self.y) ** 2)
            return distance <= self.radius + 5  # Small margin for easier clicking
        except Exception:
            return False
    
    def get_info(self):
        """Return packet information as dictionary"""
        return {
            "source_ip": self.source_ip,
            "dest_ip": self.dest_ip,
            "protocol": self.protocol,
            "type": self.packet_type.value,
            "position": (int(self.x), int(self.y)),
            "is_blocked": self.is_blocked,
            "reached_target": self.reached_target
        }
    
    def get_damage(self):
        """Return damage value based on packet type"""
        damage_map = {
            PacketType.MALICIOUS: 8,
            PacketType.SUSPICIOUS: 3,
            PacketType.SAFE: 0,
            PacketType.BLOCKED: 0
        }
        return damage_map.get(self.packet_type, 0)


# ============================================
# NETWORK NODE CLASS
# ============================================

class NetworkNode(pygame.sprite.Sprite):
    """
    Represents a network node (server, router, workstation).
    Packets travel between these nodes.
    """
    
    # Node type constants
    SERVER = "server"
    ROUTER = "router"
    WORKSTATION = "workstation"
    FIREWALL = "firewall"
    
    def __init__(self, x, y, node_type=None, name="Node"):
        """
        Initialize a network node.
        
        Args:
            x: X position
            y: Y position
            node_type: Type of node (SERVER, ROUTER, etc.)
            name: Display name for the node
        """
        super().__init__()
        
        # Position
        self.x = x
        self.y = y
        
        # Properties
        self.node_type = node_type or self.SERVER
        self.name = name
        self.health = 100
        self.is_under_attack = False
        
        # Visual properties
        self.size = self._get_size()
        self.color = self._get_color()
        self.pulse_phase = 0
        
        # Create surface
        self._create_surface()
    
    def _get_size(self):
        """Get node size based on type"""
        sizes = {
            self.SERVER: 50,
            self.ROUTER: 40,
            self.WORKSTATION: 35,
            self.FIREWALL: 45
        }
        return sizes.get(self.node_type, 40)
    
    def _get_color(self):
        """Get node color based on type"""
        colors = {
            self.SERVER: (0, 150, 220),
            self.ROUTER: (150, 0, 200),
            self.WORKSTATION: (0, 180, 100),
            self.FIREWALL: (255, 100, 50)
        }
        return colors.get(self.node_type, (100, 100, 100))
    
    def _create_surface(self):
        """Create the node surface"""
        try:
            padding = 30
            total_size = self.size + padding * 2
            self.image = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
            self.rect = self.image.get_rect(center=(self.x, self.y))
            self._draw_node()
        except pygame.error as e:
            print(f"[ERROR] Failed to create node surface: {e}")
    
    def _draw_node(self):
        """Draw the network node"""
        try:
            self.image.fill((0, 0, 0, 0))
            center = self.image.get_width() // 2
            
            # Status ring color
            if self.health > 70:
                ring_color = (0, 255, 100)
            elif self.health > 30:
                ring_color = (255, 200, 0)
            else:
                ring_color = (255, 50, 50)
            
            # Draw outer ring
            pygame.draw.circle(
                self.image, ring_color,
                (center, center), 
                self.size // 2 + 8, 3
            )
            
            # Draw node body based on type
            if self.node_type == self.SERVER:
                self._draw_server_icon(center)
            elif self.node_type == self.FIREWALL:
                self._draw_firewall_icon(center)
            else:
                self._draw_generic_icon(center)
            
            # Draw name label
            self._draw_label(center)
            
            # Attack indicator
            if self.is_under_attack:
                pulse = abs(math.sin(self.pulse_phase)) * 30
                attack_color = (255, 50, 50, int(100 + pulse))
                pygame.draw.circle(
                    self.image, attack_color,
                    (center, center),
                    self.size // 2 + 15, 2
                )
                
        except Exception as e:
            print(f"[ERROR] Failed to draw node: {e}")
    
    def _draw_server_icon(self, center):
        """Draw server-style icon"""
        size = self.size
        rect = pygame.Rect(
            center - size // 3, 
            center - size // 2,
            size // 1.5, 
            size
        )
        pygame.draw.rect(self.image, self.color, rect, border_radius=5)
        pygame.draw.rect(self.image, (255, 255, 255), rect, 2, border_radius=5)
        
        # Server lines
        for i in range(3):
            y_pos = center - size // 3 + i * (size // 4)
            pygame.draw.line(
                self.image, (255, 255, 255),
                (center - size // 4, y_pos),
                (center + size // 4, y_pos), 1
            )
            # LED indicator
            pygame.draw.circle(
                self.image, (0, 255, 100),
                (center + size // 4 - 5, y_pos), 3
            )
    
    def _draw_firewall_icon(self, center):
        """Draw firewall shield icon"""
        size = self.size
        points = [
            (center, center - size // 2),
            (center + size // 2, center - size // 4),
            (center + size // 2, center + size // 4),
            (center, center + size // 2),
            (center - size // 2, center + size // 4),
            (center - size // 2, center - size // 4)
        ]
        pygame.draw.polygon(self.image, self.color, points)
        pygame.draw.polygon(self.image, (255, 255, 255), points, 2)
    
    def _draw_generic_icon(self, center):
        """Draw generic node icon"""
        pygame.draw.circle(
            self.image, self.color,
            (center, center), self.size // 2
        )
        pygame.draw.circle(
            self.image, (255, 255, 255),
            (center, center), self.size // 2, 2
        )
    
    def _draw_label(self, center):
        """Draw node name label"""
        try:
            font = pygame.font.Font(None, 18)
            label = font.render(self.name, True, (200, 210, 230))
            label_rect = label.get_rect(
                center=(center, center + self.size // 2 + 15)
            )
            self.image.blit(label, label_rect)
        except Exception:
            pass
    
    def update(self):
        """Update node animation"""
        self.pulse_phase += 0.1
        self._draw_node()
    
    def take_damage(self, amount):
        """Reduce node health"""
        self.health = max(0, self.health - amount)
        if self.health < 50:
            self.is_under_attack = True
    
    def heal(self, amount):
        """Restore node health"""
        self.health = min(100, self.health + amount)
        if self.health > 70:
            self.is_under_attack = False


# ============================================
# PARTICLE EFFECT CLASS
# ============================================

class Particle:
    """Single particle for explosion/block effects"""
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        
        # Random velocity
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        
        # Lifetime
        self.lifetime = random.randint(20, 40)
        self.max_lifetime = self.lifetime
        self.size = random.randint(2, 5)
    
    def update(self):
        """Update particle position"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity
        self.lifetime -= 1
        return self.lifetime > 0
    
    def draw(self, surface):
        """Draw the particle"""
        try:
            if self.lifetime <= 0:
                return
            
            alpha = int((self.lifetime / self.max_lifetime) * 255)
            size = max(1, int(self.size * (self.lifetime / self.max_lifetime)))
            
            particle_surface = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(
                particle_surface, color_with_alpha,
                (size, size), size
            )
            surface.blit(particle_surface, (int(self.x) - size, int(self.y) - size))
        except Exception:
            pass


class ParticleSystem:
    """Manages multiple particles for effects"""
    
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, color, count=15):
        """Create particles at position"""
        for _ in range(count):
            self.particles.append(Particle(x, y, color))
    
    def emit_block_effect(self, x, y):
        """Special effect for blocking"""
        self.emit(x, y, (255, 50, 80), 20)
        self.emit(x, y, (255, 150, 0), 10)
    
    def emit_hit_effect(self, x, y):
        """Effect when target is hit"""
        self.emit(x, y, (255, 50, 50), 15)
    
    def update(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, surface):
        """Draw all particles"""
        for particle in self.particles:
            particle.draw(surface)


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("sprites.py - Packet Sprite Module")
    print("This module should be imported, not run directly.")
    print("Classes available: PacketSprite, NetworkNode, ParticleSystem")
