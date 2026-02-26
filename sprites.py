"""
===========================================================
PACKET DEFENDER - Sprite System
===========================================================
PacketType = visual (SAFE / SUSPICIOUS / MALICIOUS)
Attack type = from firewall.py AttackDatabase
Network nodes pulse on hit/block (#25)
===========================================================
"""

import pygame
import random
import math
from enum import Enum


# ─────────────────────────────────────────────
#  PACKET TYPE (visual only)
# ─────────────────────────────────────────────

class PacketType(Enum):
    SAFE       = "safe"
    SUSPICIOUS = "suspicious"
    MALICIOUS  = "malicious"


# ─────────────────────────────────────────────
#  VISUAL CONFIG
# ─────────────────────────────────────────────

PACKET_VISUALS = {
    PacketType.SAFE: {
        'color':   (0, 150, 255),
        'glow':    (0, 80, 180),
        'size':    5,
        'speed':   1.0,
        'damage':  0,
        'hostile': False,
    },
    PacketType.SUSPICIOUS: {
        'color':   (255, 200, 0),
        'glow':    (180, 140, 0),
        'size':    6,
        'speed':   1.3,
        'damage':  2,
        'hostile': True,
    },
    PacketType.MALICIOUS: {
        'color':   (255, 50, 50),
        'glow':    (180, 20, 20),
        'size':    7,
        'speed':   1.5,
        'damage':  5,
        'hostile': True,
    },
}


# ─────────────────────────────────────────────
#  PACKET SPRITE
# ─────────────────────────────────────────────

class PacketSprite(pygame.sprite.Sprite):
    """
    Attributes set by main.py:
        attack_id       : str
        threat_name     : str
        threat_color    : tuple
        threat_severity : str
        threat_damage   : int
        threat_icon     : str
    """
    
    # Class-level cache for pre-rendered packet images
    _image_cache = {}

    def __init__(self, sx, sy, tx, ty, ptype, ip="0.0.0.0"):
        super().__init__()
        self.packet_type = ptype
        self.source_ip = ip
        self.visuals = PACKET_VISUALS.get(ptype, PACKET_VISUALS[PacketType.SAFE])

        # Attack data (set by main.py)
        self.attack_id       = "SAFE"
        self.threat_name     = "Normal"
        self.threat_color    = self.visuals['color']
        self.threat_severity = "NONE"
        self.threat_damage   = self.visuals['damage']
        self.threat_icon     = ""

        # Position
        self.x = float(sx)
        self.y = float(sy)
        self.target_x = float(tx)
        self.target_y = float(ty)

        dx = tx - sx
        dy = ty - sy
        dist = max(math.hypot(dx, dy), 1)
        spd = (1.5 + random.random() * 0.5) * self.visuals['speed']
        self.vx = (dx / dist) * spd
        self.vy = (dy / dist) * spd

        # State
        self.reached_target = False
        self.is_blocked = False
        self.alpha = 255
        self.trail = []
        self.pulse = random.random() * 6.28
        self.block_rule = None

        # Surface setup
        self._set_image()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _get_cache_key(self):
        return (self.packet_type, self.threat_color)

    def _set_image(self):
        key = self._get_cache_key()
        if key not in PacketSprite._image_cache:
            sz = self.visuals['size'] * 2 + 10
            img = pygame.Surface((sz, sz), pygame.SRCALPHA)
            s = self.visuals['size']
            cx = sz // 2
            cy = sz // 2

            # Glow
            gs = pygame.Surface((s * 4, s * 4), pygame.SRCALPHA)
            gc = self.visuals.get('glow', (100, 100, 100))
            pygame.draw.circle(gs, (gc[0], gc[1], gc[2], 60), (s*2, s*2), s*2)
            img.blit(gs, (cx - s*2, cy - s*2))

            # Main dot
            color = self.threat_color if self.threat_color else self.visuals['color']
            pygame.draw.circle(img, color, (cx, cy), s)

            # Center highlight
            pygame.draw.circle(img, (255, 255, 255, 180), (cx, cy), max(2, s//2))
            
            PacketSprite._image_cache[key] = img
            
        self.image = PacketSprite._image_cache[key]

    def recolor(self, color, glow=None):
        self.threat_color = color
        self._set_image()

    def update(self, speed_scale=1.0):
        if self.is_blocked:
            self.alpha = max(0, self.alpha - 20)
            self.image.set_alpha(self.alpha)
            return

        if self.reached_target:
            return

        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 4:
            self.trail.pop(0)

        self.x += self.vx * speed_scale
        self.y += self.vy * speed_scale
        self.rect.center = (int(self.x), int(self.y))
        self.pulse += 0.15 * speed_scale

        if math.hypot(self.target_x - self.x, self.target_y - self.y) < 15:
            self.reached_target = True

    # Cache for trail surfaces
    _trail_cache = {}

    def draw_trail(self, screen):
        if self.is_blocked or not self.trail:
            return
            
        c = self.threat_color
        key = (c, self.visuals['size'])
        
        if key not in PacketSprite._trail_cache:
            r = self.visuals['size']
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (c[0], c[1], c[2], 40), (r, r), r)
            PacketSprite._trail_cache[key] = s
            
        trail_img = PacketSprite._trail_cache[key]
        n = len(self.trail)
        for i, (tx, ty) in enumerate(self.trail):
            screen.blit(trail_img, (tx - self.visuals['size'], ty - self.visuals['size']))

    def block(self, rule_name=None):
        self.is_blocked = True
        self.block_rule = rule_name
        self.image = self.image.copy()

    def contains_point(self, pos):
        return math.hypot(pos[0] - self.x, pos[1] - self.y) < self.visuals['size'] + 10

    def get_damage(self):
        if self.threat_damage > 0:
            return self.threat_damage
        return self.visuals['damage']

    def is_hostile(self):
        return self.packet_type in (PacketType.SUSPICIOUS, PacketType.MALICIOUS)


# ─────────────────────────────────────────────
#  NETWORK NODE (with animation #25)
# ─────────────────────────────────────────────

class NetworkNode(pygame.sprite.Sprite):
    SERVER      = 'server'
    FIREWALL    = 'firewall'
    ROUTER      = 'router'
    WORKSTATION = 'workstation'

    COLORS = {
        'server':      (0, 200, 100),
        'firewall':    (255, 100, 0),
        'router':      (0, 150, 255),
        'workstation': (150, 150, 200),
    }

    def __init__(self, x, y, ntype, name=""):
        super().__init__()
        self.x = x
        self.y = y
        self.node_type = ntype
        self.name = name
        self.pulse = random.random() * 6.28

        # Animation state (#25)
        self.hit_flash = 0       # Red flash when hit
        self.block_flash = 0     # Green flash when blocks
        self.base_glow = 0.0     # Ambient glow
        self.activity = 0.0      # Activity level 0-1

        sz = {'server': 50, 'firewall': 44, 'router': 38}.get(ntype, 34)
        self.node_size = sz
        self.image = pygame.Surface((sz + 20, sz + 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))
        self._base_color = self.COLORS.get(ntype, (150, 150, 150))
        self._render()

    def trigger_hit(self):
        """Call when a malicious packet hits the server"""
        self.hit_flash = 20

    def trigger_block(self):
        """Call when firewall successfully blocks a packet"""
        self.block_flash = 15

    def set_activity(self, level):
        """Set activity level 0.0 to 1.0"""
        self.activity = max(0.0, min(1.0, level))

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        c = self._base_color
        sz = self.node_size
        offset = 10
        cx = sz // 2 + offset
        cy = sz // 2 + offset

        # Ambient glow ring
        glow_alpha = int(20 + 10 * self.activity)
        pygame.draw.circle(
            self.image, (c[0], c[1], c[2], min(60, glow_alpha)),
            (cx, cy), sz // 2 + 5
        )

        # Base circle
        pygame.draw.circle(self.image, (c[0], c[1], c[2], 30), (cx, cy), sz // 2)

        if self.node_type == self.SERVER:
            pygame.draw.rect(self.image, c, (cx-12, cy-15, 24, 30), border_radius=3)
            pygame.draw.rect(self.image, (255,255,255,140), (cx-12, cy-15, 24, 30), 2, border_radius=3)
            for i in range(3):
                pygame.draw.circle(self.image, (255,255,255,180), (cx, cy-8+i*8), 2)

        elif self.node_type == self.FIREWALL:
            pts = [(cx, cy-16), (cx+16, cy), (cx, cy+16), (cx-16, cy)]
            pygame.draw.polygon(self.image, c, pts)
            pygame.draw.polygon(self.image, (255,255,255,140), pts, 2)
            pygame.draw.circle(self.image, (255, 200, 0), (cx, cy), 4)

        elif self.node_type == self.ROUTER:
            pygame.draw.circle(self.image, c, (cx, cy), 14)
            pygame.draw.circle(self.image, (255,255,255,140), (cx, cy), 14, 2)
            for a in [0, 90, 180, 270]:
                r = math.radians(a)
                pygame.draw.line(
                    self.image, (255,255,255,180),
                    (cx, cy),
                    (cx + int(10*math.cos(r)), cy + int(10*math.sin(r))), 2
                )

        else:
            pygame.draw.rect(self.image, c, (cx-10, cy-8, 20, 16), border_radius=2)
            pygame.draw.rect(self.image, (255,255,255,140), (cx-10, cy-8, 20, 16), 1, border_radius=2)
            pygame.draw.rect(self.image, (100,200,255,100), (cx-7, cy-5, 14, 8))

    def update(self):
        self.pulse += 0.05
        old_hit = self.hit_flash
        old_block = self.block_flash
        old_act = int(self.activity * 10)

        # Decrease flash timers
        if self.hit_flash > 0:
            self.hit_flash -= 1
        if self.block_flash > 0:
            self.block_flash -= 1

        # Smooth activity decay
        self.activity *= 0.98

        # Only re-render if something changed visually
        if old_hit != self.hit_flash or old_block != self.block_flash or old_act != int(self.activity * 10):
            self._render()

            sz = self.node_size
            offset = 10
            cx = sz // 2 + offset
            cy = sz // 2 + offset

            # Hit flash — red ring
            if self.hit_flash > 0:
                flash_alpha = min(200, self.hit_flash * 12)
                ring_radius = sz // 2 + 3 + (20 - self.hit_flash)
                ring_surf = pygame.Surface(
                    (ring_radius*2+4, ring_radius*2+4), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    ring_surf, (255, 50, 50, flash_alpha),
                    (ring_radius+2, ring_radius+2), ring_radius, 3
                )
                self.image.blit(
                    ring_surf,
                    (cx - ring_radius - 2, cy - ring_radius - 2)
                )

            # Block flash — green ring
            if self.block_flash > 0:
                flash_alpha = min(180, self.block_flash * 14)
                ring_radius = sz // 2 + 2 + (15 - self.block_flash)
                ring_surf = pygame.Surface(
                    (ring_radius*2+4, ring_radius*2+4), pygame.SRCALPHA
                )
                pygame.draw.circle(
                    ring_surf, (0, 255, 100, flash_alpha),
                    (ring_radius+2, ring_radius+2), ring_radius, 2
                )
                self.image.blit(
                    ring_surf,
                    (cx - ring_radius - 2, cy - ring_radius - 2)
                )

            # Name label
            try:
                font = pygame.font.Font(None, 14)
                name_color = (200, 200, 200)
                if self.hit_flash > 0:
                    name_color = (255, 100, 100)
                elif self.block_flash > 0:
                    name_color = (100, 255, 100)

                nt = font.render(self.name, True, name_color)
                nx = cx - nt.get_width() // 2
                ny = cy + sz // 2 + 2
                if ny + nt.get_height() < self.image.get_height():
                    self.image.blit(nt, (nx, ny))
            except Exception:
                pass


# ─────────────────────────────────────────────
#  CONNECTION LINE ANIMATOR (#25)
# ─────────────────────────────────────────────

class ConnectionAnimator:
    """
    Draws animated connection lines between network nodes.
    Flashes red when packet hits, green when blocked.
    """

    def __init__(self):
        self.connections = []  # list of (node1, node2, base_color)
        self.flashes = []     # list of {from, to, color, timer, max_timer}

    def set_connections(self, conn_list):
        """conn_list: [(node1, node2, color), ...]"""
        self.connections = conn_list

    def flash_line(self, node_from, node_to, color, duration=15):
        """Trigger a colored flash on a connection line"""
        self.flashes.append({
            'from': node_from,
            'to': node_to,
            'color': color,
            'timer': duration,
            'max_timer': duration,
        })

    def flash_hit(self, node_from, node_to):
        """Red flash — packet hit server"""
        self.flash_line(node_from, node_to, (255, 50, 50), 12)

    def flash_block(self, node_from, node_to):
        """Green flash — packet blocked at firewall"""
        self.flash_line(node_from, node_to, (0, 255, 100), 10)

    def update(self):
        self.flashes = [f for f in self.flashes if f['timer'] > 0]
        for f in self.flashes:
            f['timer'] -= 1

    def draw(self, screen):
        # Draw base connections
        for n1, n2, base_color in self.connections:
            pygame.draw.line(screen, base_color, (n1.x, n1.y), (n2.x, n2.y), 2)

        # Draw flash overlays
        for f in self.flashes:
            n1 = f['from']
            n2 = f['to']
            t = f['timer'] / max(1, f['max_timer'])

            alpha = int(200 * t)
            width = int(2 + 4 * t)

            color = f['color']

            # Draw thick glowing line
            try:
                # Main line
                pygame.draw.line(screen, color, (n1.x, n1.y), (n2.x, n2.y), width)

                # Glow effect
                glow_surf = pygame.Surface(
                    (abs(n2.x - n1.x) + 20, abs(n2.y - n1.y) + 20),
                    pygame.SRCALPHA
                )
                ox = min(n1.x, n2.x) - 10
                oy = min(n1.y, n2.y) - 10
                pygame.draw.line(
                    glow_surf,
                    (color[0], color[1], color[2], alpha // 3),
                    (n1.x - ox, n1.y - oy),
                    (n2.x - ox, n2.y - oy),
                    width + 4
                )
                screen.blit(glow_surf, (ox, oy))
            except Exception:
                pass

            # Moving pulse dot along the line
            try:
                progress = 1.0 - t  # 0 → 1 over duration
                px = int(n1.x + (n2.x - n1.x) * progress)
                py = int(n1.y + (n2.y - n1.y) * progress)
                dot_r = int(3 + 3 * t)
                pygame.draw.circle(screen, color, (px, py), dot_r)
                # Dot glow
                dot_glow = pygame.Surface((dot_r*4, dot_r*4), pygame.SRCALPHA)
                pygame.draw.circle(
                    dot_glow,
                    (color[0], color[1], color[2], alpha // 2),
                    (dot_r*2, dot_r*2), dot_r*2
                )
                screen.blit(dot_glow, (px - dot_r*2, py - dot_r*2))
            except Exception:
                pass


# ─────────────────────────────────────────────
#  BOOSTER SPRITE
# ─────────────────────────────────────────────

class BoosterType(Enum):
    HEAL         = "HEAL"
    DOUBLE_SCORE = "DOUBLE"
    PURGE        = "PURGE"
    SLOW_MO      = "SLOW"
    AUTO_BLOCK   = "AUTO"

class BoosterSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, btype):
        super().__init__()
        self.btype = btype
        self.x = float(x)
        self.y = float(y)
        
        # Random floating movement
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(0.5, 1.5)
        
        if btype == BoosterType.HEAL:
            self.color = (0, 255, 100)
            self.glow = (0, 100, 40)
            self.icon = "+"
        elif btype == BoosterType.DOUBLE_SCORE:
            self.color = (255, 215, 0)
            self.glow = (100, 85, 0)
            self.icon = "x2"
        elif btype == BoosterType.PURGE:
            self.color = (255, 50, 50)
            self.glow = (120, 20, 20)
            self.icon = "!!!"
        elif btype == BoosterType.SLOW_MO:
            self.color = (180, 0, 255)
            self.glow = (80, 0, 120)
            self.icon = "~"
        elif btype == BoosterType.AUTO_BLOCK:
            self.color = (0, 180, 255)
            self.glow = (0, 60, 120)
            self.icon = "SHLD"
        
        self.alpha = 255
        self.life = 480  # 8 seconds at 60fps
        self.pulse = 0.0
        
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(x), int(y)))
        self._render()

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx, cy = 20, 20
        r = 15 + 2 * math.sin(self.pulse)
        
        # Outer Glow
        for i in range(5):
            pygame.draw.circle(self.image, (*self.glow, 40 - i * 8), (cx, cy), r + 4 - i)
            
        # Circle
        pygame.draw.circle(self.image, self.color, (cx, cy), r, 2)
        
        # Icon
        font = pygame.font.Font(None, 24)
        it = font.render(self.icon, True, self.color)
        self.image.blit(it, (cx - it.get_width()//2, cy - it.get_height()//2))

    def update(self):
        self.pulse += 0.1
        self.life -= 1
        if self.life <= 0:
            self.kill()
            return

        if self.life < 60:
            self.alpha = int(255 * (self.life / 60))
            
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off screen edges
        if self.x < 260 or self.x > 940: self.vx *= -1
        if self.y > 540: self.vy *= -1
        if self.y < 50: self.vy *= -1
            
        self.rect.center = (int(self.x), int(self.y))

    def draw(self, screen):
        self._render()
        self.image.set_alpha(self.alpha)
        screen.blit(self.image, self.rect)


    def contains_point(self, pos):
        return math.hypot(pos[0] - self.x, pos[1] - self.y) < 20


# ─────────────────────────────────────────────
#  INTEL SPRITE
# ─────────────────────────────────────────────

class IntelType(Enum):
    STANDARD = "STANDARD"
    LARGE    = "LARGE"

class IntelSprite(pygame.sprite.Sprite):
    """Cyber Intel collectibles (Data Chips)"""
    def __init__(self, x, itype=IntelType.STANDARD):
        super().__init__()
        self.itype = itype
        self.x = float(x)
        self.y = -30.0 # Start above screen
        
        # Move downwards
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = random.uniform(2.0, 3.5)
        
        if itype == IntelType.LARGE:
            self.size = 24
            self.color = (0, 255, 255) # Cyan
            self.points = 100
            self.label = "INTEL+"
        else:
            self.size = 16
            self.color = (0, 200, 255) # Light Blue
            self.points = 50
            self.label = "INTEL"
            
        self.glow = (0, 80, 100)
        self.pulse = 0.0
        self.alpha = 255
        self.life = 600
        
        self.image = pygame.Surface((self.size * 2 + 10, self.size * 2 + 10), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        self._render()

    def _render(self):
        self.image.fill((0, 0, 0, 0))
        cx = self.image.get_width() // 2
        cy = self.image.get_height() // 2
        r = self.size + 2 * math.sin(self.pulse)
        
        # Hexagon/Chip shape
        pts = []
        for i in range(6):
            angle = math.radians(i * 60 + (self.pulse * 10))
            px = cx + r * math.cos(angle)
            py = cy + r * math.sin(angle)
            pts.append((px, py))
            
        # Glow
        pygame.draw.circle(self.image, (*self.glow, 40), (cx, cy), r + 5)
        
        # Main shape
        pygame.draw.polygon(self.image, self.color, pts)
        pygame.draw.polygon(self.image, (255, 255, 255, 180), pts, 2)
        
        # Interior pattern (Chip look)
        pygame.draw.line(self.image, (255,255,255,100), (cx-r//2, cy), (cx+r//2, cy), 1)
        pygame.draw.line(self.image, (255,255,255,100), (cx, cy-r//2), (cx, cy+r//2), 1)

    def update(self, speed_scale=1.0):
        self.pulse += 0.05 * speed_scale
        
        self.x += self.vx * speed_scale
        self.y += self.vy * speed_scale
        
        self.rect.center = (int(self.x), int(self.y))
        
        # Kill if off screen
        if self.y > 750:
            self.kill()

    def draw(self, screen):
        self._render()
        self.image.set_alpha(self.alpha)
        screen.blit(self.image, self.rect)


    def contains_point(self, pos):
        # Slightly larger hitbox for better feel
        return math.hypot(pos[0] - self.x, pos[1] - self.y) < self.size + 15


# ─────────────────────────────────────────────
#  PARTICLE
# ─────────────────────────────────────────────

class Particle:
    __slots__ = ('x', 'y', 'color', 'dx', 'dy', 'life', 'max_life')
    
    # Pre-rendered cache: (color, size, alpha) -> Surface
    _cache = {}

    def __init__(self, x, y, color, dx, dy, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.dx = dx
        self.dy = dy
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.dx *= 0.94
        self.dy *= 0.94
        self.life -= 1

    def draw(self, screen):
        if self.life <= 0:
            return
        
        # Round life/max_life to reduce cache entries
        alpha_step = max(1, self.life * 5 // self.max_life) # 0 to 5
        alpha = int(255 * alpha_step / 5)
        r = max(1, int(3 * self.life / self.max_life))
        
        key = (self.color, r, alpha)
        if key not in Particle._cache:
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (self.color[0], self.color[1], self.color[2], alpha), (r, r), r)
            Particle._cache[key] = s
        
        screen.blit(Particle._cache[key], (int(self.x) - r, int(self.y) - r))


# ─────────────────────────────────────────────
#  PARTICLE SYSTEM
# ─────────────────────────────────────────────

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.max_particles = 1000 # Safety limit

    def clear(self):
        self.particles.clear()

    def emit_block_effect(self, x, y):
        if len(self.particles) > self.max_particles: return
        for _ in range(12):
            a = random.random() * 6.28
            sp = random.random() * 4 + 1
            c = random.choice([(255,100,0), (255,200,0), (255,50,50)])
            self.particles.append(
                Particle(x, y, c, math.cos(a)*sp, math.sin(a)*sp, random.randint(15, 35))
            )

    def emit_hit_effect(self, x, y):
        if len(self.particles) > self.max_particles: return
        for _ in range(8):
            a = random.random() * 6.28
            sp = random.random() * 3 + 0.5
            self.particles.append(
                Particle(x, y, (255,0,0), math.cos(a)*sp, math.sin(a)*sp, random.randint(10, 25))
            )

    def emit_success_effect(self, x, y):
        """Green particles for successful block"""
        if len(self.particles) > self.max_particles: return
        for _ in range(10):
            a = random.random() * 6.28
            sp = random.random() * 3 + 1
            c = random.choice([(0,255,100), (0,200,80), (100,255,150)])
            self.particles.append(
                Particle(x, y, c, math.cos(a)*sp, math.sin(a)*sp, random.randint(12, 28))
            )

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()

    def draw(self, screen):
        for p in self.particles:
            p.draw(screen)
