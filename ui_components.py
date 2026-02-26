"""
===========================================================
UI COMPONENTS - Packet Defender
===========================================================
Menu Screen | Paginated Firewall Panel | Encyclopedia
Live Terminal | Briefing | Post-Wave Report
Smart Suggestions | Wave Progress | Attack Popup
All colors safe-clamped
===========================================================
"""

import pygame
import math
import time
import random


# ─────────────────────────────────────────────
#  SAFE COLOR
# ─────────────────────────────────────────────

def safe_color(r, g, b, a=None):
    r, g, b = max(0,min(255,int(r))), max(0,min(255,int(g))), max(0,min(255,int(b)))
    if a is not None:
        return (r, g, b, max(0,min(255,int(a))))
    return (r, g, b)

def safe_rgba(color, alpha):
    try: return safe_color(color[0], color[1], color[2], alpha)
    except: return (255, 255, 255, max(0,min(255,int(alpha))))


# ─────────────────────────────────────────────
#  THEME
# ─────────────────────────────────────────────

class Theme:
    NEON_BLUE    = (0, 180, 255)
    NEON_GREEN   = (0, 255, 100)
    NEON_RED     = (255, 50, 50)
    NEON_YELLOW  = (255, 220, 0)
    NEON_ORANGE  = (255, 150, 0)
    NEON_PURPLE  = (180, 0, 255)
    NEON_CYAN    = (0, 255, 255)
    NEON_PINK    = (255, 0, 180)

    PANEL_BG     = (15, 22, 38)
    PANEL_HOVER  = (25, 38, 60)
    PANEL_ACTIVE = (30, 45, 70)
    PANEL_DARK   = (8, 12, 22)

    TEXT_PRIMARY   = (220, 230, 240)
    TEXT_SECONDARY = (120, 140, 160)
    TEXT_DIM       = (70, 85, 100)
    TEXT_BRIGHT    = (255, 255, 255)

    STATUS_ON  = (0, 255, 100)
    STATUS_OFF = (255, 60, 60)

    TIER_COLORS = {1: (0,180,255), 2: (255,180,0), 3: (180,0,255), 4: (255,60,60)}

    @staticmethod
    def tier_color(t): return Theme.TIER_COLORS.get(t, Theme.TEXT_SECONDARY)

    @staticmethod
    def severity_color(s):
        return {"CRITICAL":(255,0,0),"HIGH":(255,80,0),"MEDIUM":(255,200,0),"LOW":(100,200,100)}.get(s, Theme.TEXT_SECONDARY)


# ═══════════════════════════════════════════════
#  MENU SCREEN
# ═══════════════════════════════════════════════

class MenuScreen:
    """Start screen before game begins"""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.visible = True
        self.pulse = 0.0
        self.selected = 0  # 0=start, 1=quit

        self.title_font = pygame.font.Font(None, 72)
        self.sub_font = pygame.font.Font(None, 32)
        self.btn_font = pygame.font.Font(None, 36)
        self.info_font = pygame.font.Font(None, 20)
        self.tip_font = pygame.font.Font(None, 18)

        bw, bh = 240, 50
        cx = width // 2
        self.btn_start = pygame.Rect(cx - bw//2, 300, bw, bh)
        self.btn_quit = pygame.Rect(cx - bw//2, 365, bw, bh)

    def handle_click(self, mpos):
        if not self.visible:
            return None
        if self.btn_start.collidepoint(mpos):
            self.visible = False
            return "START"
        if self.btn_quit.collidepoint(mpos):
            return "QUIT"
        return None

    def handle_key(self, key):
        if not self.visible:
            return None
        if key == pygame.K_RETURN or key == pygame.K_SPACE:
            self.visible = False
            return "START"
        if key == pygame.K_ESCAPE:
            return "QUIT"
        return None

    def update(self):
        self.pulse = (self.pulse + 0.03) % (2 * math.pi)

    def draw(self, screen):
        if not self.visible:
            return

        screen.fill((5, 8, 15))

        # Grid background
        for x in range(0, self.w, 50):
            pygame.draw.line(screen, (15, 20, 35), (x, 0), (x, self.h))
        for y in range(0, self.h, 50):
            pygame.draw.line(screen, (15, 20, 35), (0, y), (self.w, y))

        cx = self.w // 2

        # Title with pulse
        p = abs(math.sin(self.pulse))
        tc = safe_color(0 + 180*p, 150 + 50*p, 200 + 55*p)
        title = self.title_font.render("PACKET DEFENDER", True, tc)
        screen.blit(title, (cx - title.get_width()//2, 80))

        # Subtitle
        sub = self.sub_font.render("Cyber Defense Simulation", True, Theme.TEXT_SECONDARY)
        screen.blit(sub, (cx - sub.get_width()//2, 150))

        # Divider
        pygame.draw.line(screen, Theme.NEON_BLUE, (cx-150, 190), (cx+150, 190), 2)

        # Info
        info_lines = [
            "Defend your network against real cyber attacks",
            "Enable firewall rules to block threats",
            "Survive 3 waves to secure the network",
        ]
        y = 215
        for line in info_lines:
            t = self.info_font.render(line, True, Theme.TEXT_PRIMARY)
            screen.blit(t, (cx - t.get_width()//2, y))
            y += 24

        # Start button
        mpos = pygame.mouse.get_pos()
        s_hover = self.btn_start.collidepoint(mpos)
        s_bg = (0, 60, 40) if s_hover else (10, 30, 20)
        pygame.draw.rect(screen, s_bg, self.btn_start, border_radius=10)
        pygame.draw.rect(screen, Theme.NEON_GREEN, self.btn_start, 3, border_radius=10)
        st = self.btn_font.render("START GAME", True, Theme.NEON_GREEN)
        screen.blit(st, (self.btn_start.centerx - st.get_width()//2,
                         self.btn_start.centery - st.get_height()//2))

        # Quit button
        q_hover = self.btn_quit.collidepoint(mpos)
        q_bg = (50, 15, 15) if q_hover else (30, 10, 10)
        pygame.draw.rect(screen, q_bg, self.btn_quit, border_radius=10)
        pygame.draw.rect(screen, Theme.NEON_RED, self.btn_quit, 2, border_radius=10)
        qt = self.btn_font.render("QUIT", True, Theme.NEON_RED)
        screen.blit(qt, (self.btn_quit.centerx - qt.get_width()//2,
                         self.btn_quit.centery - qt.get_height()//2))

        # Controls hint
        tips = [
            "[Q] Block  [E] Heal  [C] Clear  [F] Firewall  [I] Encyclopedia",
            "[SPACE] Pause  [A] Auto Mode  [R] Restart",
        ]
        y = 440
        for tip in tips:
            t = self.tip_font.render(tip, True, Theme.TEXT_DIM)
            screen.blit(t, (cx - t.get_width()//2, y))
            y += 22

        # Version
        vt = self.tip_font.render("v2.0 | Rule-Based Firewall Edition", True, Theme.TEXT_DIM)
        screen.blit(vt, (cx - vt.get_width()//2, self.h - 30))

        # Legend/Tutorial Section
        self._draw_legend(screen)

    def _draw_legend(self, screen):
        lx = 50
        ly = self.h - 180
        title = self.sub_font.render("NETWORK OBJECTS", True, Theme.NEON_CYAN)
        screen.blit(title, (lx, ly))
        
        items = [
            ("CHIP", Theme.NEON_BLUE, "Intel: +50/100 Points"),
            ("+", Theme.NEON_GREEN, "Heal: Restore 10 HP"),
            ("x2", Theme.NEON_YELLOW, "Double Score (10s)"),
            ("!!!", Theme.NEON_RED, "Purge: Clear Packets"),
            ("~", Theme.NEON_PURPLE, "Slow: Time Dilation"),
            ("SHLD", Theme.NEON_BLUE, "Auto-Block (3s)")
        ]
        
        y = ly + 35
        for icon, color, desc in items:
            # Icon box
            pygame.draw.rect(screen, color, (lx, y, 40, 20), 1, border_radius=4)
            it = self.tip_font.render(icon, True, color)
            screen.blit(it, (lx + 20 - it.get_width()//2, y + 10 - it.get_height()//2))
            
            # Description
            dt = self.tip_font.render(desc, True, Theme.TEXT_SECONDARY)
            screen.blit(dt, (lx + 50, y + 3))
            y += 24


# ═══════════════════════════════════════════════
#  HEALTH BAR
# ═══════════════════════════════════════════════

class HealthBar:
    def __init__(self, x, y, w, h, max_val, label="HP"):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.max_val = max_val
        self.value = max_val
        self.display = float(max_val)
        self.pulse = 0.0
        self.font = pygame.font.Font(None, 16)
        self.fv = pygame.font.Font(None, 18)

    def set_value(self, v): self.value = max(0, min(self.max_val, v))

    def update(self):
        self.display += (self.value - self.display) * 0.1
        self.pulse = (self.pulse + 0.08) % (2*math.pi)

    def draw(self, screen):
        pct = self.display / max(1, self.max_val)
        c = Theme.NEON_GREEN if pct > 0.6 else (Theme.NEON_YELLOW if pct > 0.3 else Theme.NEON_RED)
        if pct <= 0.3:
            a = max(0, min(255, int(40 + 30*math.sin(self.pulse*3))))
            g = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            g.fill(safe_rgba(Theme.NEON_RED, a))
            screen.blit(g, (self.x, self.y))
        pygame.draw.rect(screen, (20,25,35), (self.x, self.y, self.w, self.h), border_radius=4)
        fw = max(0, int(self.w * pct))
        if fw > 0:
            pygame.draw.rect(screen, c, (self.x, self.y, fw, self.h), border_radius=4)
        pygame.draw.rect(screen, c, (self.x, self.y, self.w, self.h), 2, border_radius=4)
        screen.blit(self.font.render("HEALTH", True, Theme.TEXT_SECONDARY), (self.x, self.y-14))
        vt = self.fv.render(f"{int(self.display)}%", True, Theme.TEXT_BRIGHT)
        screen.blit(vt, (self.x+self.w//2-vt.get_width()//2, self.y+self.h//2-vt.get_height()//2))


# ═══════════════════════════════════════════════
#  CYBER BUTTON
# ═══════════════════════════════════════════════

class CyberButton:
    def __init__(self, x, y, w, h, text, color, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.color, self.callback = text, color, callback
        self.hovered = self.pressed = False
        self.click_anim = 0
        self.font = pygame.font.Font(None, 18)

    def update(self, mpos, mpressed):
        self.hovered = self.rect.collidepoint(mpos)
        if self.hovered and mpressed[0]:
            self.pressed = True
            self.click_anim = 10
        else:
            self.pressed = False
            
        if self.click_anim > 0:
            self.click_anim -= 1

    def draw(self, screen):
        is_pressed_visual = self.pressed or self.click_anim > 0
        bg = Theme.PANEL_ACTIVE if is_pressed_visual else (Theme.PANEL_HOVER if self.hovered else Theme.PANEL_BG)
        pygame.draw.rect(screen, bg, self.rect, border_radius=6)
        if self.hovered:
            g = pygame.Surface((self.rect.w+4, self.rect.h+4), pygame.SRCALPHA)
            g.fill(safe_rgba(self.color, 30))
            screen.blit(g, (self.rect.x-2, self.rect.y-2))
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=6)
        tc = Theme.TEXT_BRIGHT if (self.hovered or is_pressed_visual) else self.color
        t = self.font.render(self.text, True, tc)
        screen.blit(t, (self.rect.centerx-t.get_width()//2, self.rect.centery-t.get_height()//2))


# ═══════════════════════════════════════════════
#  STATS PANEL
# ═══════════════════════════════════════════════

class StatsPanel:
    def __init__(self, x, y, w, h, title="STATS"):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.stats = {}
        self.ft = pygame.font.Font(None, 18)
        self.fk = pygame.font.Font(None, 16)
        self.fv = pygame.font.Font(None, 17)

    def set_stats(self, d): self.stats = d

    def draw(self, screen):
        pygame.draw.rect(screen, Theme.PANEL_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, Theme.NEON_BLUE, self.rect, 1, border_radius=5)
        screen.blit(self.ft.render(self.title, True, Theme.NEON_BLUE), (self.rect.x+8, self.rect.y+6))
        pygame.draw.line(screen, Theme.NEON_BLUE, (self.rect.x+5, self.rect.y+24), (self.rect.x+self.rect.w-5, self.rect.y+24))
        y = self.rect.y + 32
        for k, v in self.stats.items():
            screen.blit(self.fk.render(str(k), True, Theme.TEXT_SECONDARY), (self.rect.x+10, y))
            vt = self.fv.render(str(v), True, Theme.TEXT_PRIMARY)
            screen.blit(vt, (self.rect.x+self.rect.w-vt.get_width()-10, y))
            y += 20
            if y > self.rect.y+self.rect.h-10: break


# ═══════════════════════════════════════════════
#  LOG PANEL
# ═══════════════════════════════════════════════

class LogPanel:
    def __init__(self, x, y, w, h, title="LOG"):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.logs = []
        self.scroll = 0
        self.ft = pygame.font.Font(None, 28) # Increased
        self.fl = pygame.font.Font(None, 20) # Increased

    def add_log(self, msg, typ="info"):
        cm = {"info":Theme.TEXT_SECONDARY,"success":Theme.NEON_GREEN,"warning":Theme.NEON_YELLOW,
              "danger":Theme.NEON_RED,"block":Theme.NEON_ORANGE,"rule":Theme.NEON_CYAN,
              "terminal":Theme.NEON_GREEN}
        color = cm.get(typ, Theme.TEXT_SECONDARY)
        # Pre-render text
        surf = self.fl.render(msg, True, color)
        self.logs.append({"msg":msg,"color":color, "surf": surf})
        if len(self.logs) > 100: self.logs = self.logs[-100:]
        vis = max(1, (self.rect.h-40)//22)
        self.scroll = max(0, len(self.logs)-vis)

    def clear_logs(self): self.logs.clear(); self.scroll = 0

    def draw(self, screen):
        pygame.draw.rect(screen, Theme.PANEL_BG, self.rect, border_radius=5)
        pygame.draw.rect(screen, Theme.NEON_PURPLE, self.rect, 1, border_radius=5)
        screen.blit(self.ft.render(self.title, True, Theme.NEON_PURPLE), (self.rect.x+8, self.rect.y+6))
        pygame.draw.line(screen, Theme.NEON_PURPLE, (self.rect.x+5, self.rect.y+30), (self.rect.x+self.rect.w-5, self.rect.y+30))
        vis = max(1, (self.rect.h-45)//22)
        end = min(self.scroll+vis, len(self.logs))
        y = self.rect.y+38
        for i in range(self.scroll, end):
            e = self.logs[i]
            screen.blit(e["surf"], (self.rect.x+6, y))
            y += 22


# ═══════════════════════════════════════════════
#  THREAT INDICATOR
# ═══════════════════════════════════════════════

class ThreatIndicator:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.level = 0; self.display = 0.0; self.pulse = 0.0
        self.fl = pygame.font.Font(None, 14); self.fv = pygame.font.Font(None, 20)

    def set_level(self, v): self.level = max(0, min(100, v))
    def update(self):
        self.display += (self.level-self.display)*0.08
        self.pulse = (self.pulse+0.06)%(2*math.pi)

    def draw(self, screen):
        if self.display >= 80: label, c = "CRITICAL", Theme.NEON_RED
        elif self.display >= 60: label, c = "HIGH", Theme.NEON_ORANGE
        elif self.display >= 35: label, c = "MEDIUM", Theme.NEON_YELLOW
        else: label, c = "LOW", Theme.NEON_GREEN
        pygame.draw.rect(screen, Theme.PANEL_BG, self.rect, border_radius=6)
        if self.display >= 60:
            a = max(0, min(255, int(20+25*math.sin(self.pulse*3))))
            g = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
            g.fill(safe_rgba(c, a)); screen.blit(g, self.rect.topleft)
        pygame.draw.rect(screen, c, self.rect, 2, border_radius=6)
        screen.blit(self.fl.render("THREAT", True, Theme.TEXT_SECONDARY), (self.rect.x+6, self.rect.y+4))
        screen.blit(self.fv.render(label, True, c), (self.rect.x+6, self.rect.y+18))
        pt = self.fl.render(f"{int(self.display)}%", True, c)
        screen.blit(pt, (self.rect.x+self.rect.w-pt.get_width()-6, self.rect.y+20))


# ═══════════════════════════════════════════════
#  DEFENSE MODE TOGGLE
# ═══════════════════════════════════════════════

class DefenseModeToggle:
    def __init__(self, x, y, w, h, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.auto = False; self.callback = callback; self.anim = 0.0
        self.font = pygame.font.Font(None, 17)

    def toggle(self):
        self.auto = not self.auto
        try: self.callback(self.auto)
        except: pass

    def set_state(self, state):
        self.auto = state
        self.anim = 1.0 if self.auto else 0.0

    def handle_click(self, mpos):
        if self.rect.collidepoint(mpos):
            self.toggle()
            return True
        return False

    def update(self):
        self.anim = min(1.0, self.anim+0.1) if self.auto else max(0.0, self.anim-0.1)

    def draw(self, screen):
        c = Theme.NEON_GREEN if self.auto else Theme.NEON_RED
        bg = (20,40,30) if self.auto else (40,20,20)
        pygame.draw.rect(screen, bg, self.rect, border_radius=8)
        pygame.draw.rect(screen, c, self.rect, 2, border_radius=8)
        screen.blit(self.font.render("AUTO" if self.auto else "MANUAL", True, c), (self.rect.x+8, self.rect.y+5))
        st = self.font.render("ON" if self.auto else "OFF", True, c)
        screen.blit(st, (self.rect.x+self.rect.w-st.get_width()-8, self.rect.y+5))
        rx = self.rect.x+self.rect.w-35; ry = self.rect.y+self.rect.h-10
        pygame.draw.rect(screen, (40,50,60), (rx, ry-5, 30, 10), border_radius=5)
        kx = int(rx+3+self.anim*14)
        pygame.draw.circle(screen, c, (kx+5, ry), 6)


# ═══════════════════════════════════════════════
#  ACTION BUTTON GROUP
# ═══════════════════════════════════════════════

class ActionButtonGroup:
    """HUD buttons for Block, Clear, and Heal actions"""
    def __init__(self, x, y, w, h, block_cb, clear_cb, heal_cb):
        self.rect = pygame.Rect(x, y, w, h)
        bw = 90
        self.buttons = [
            CyberButton(x, y, bw, h, "BLOCK [Q]", Theme.NEON_ORANGE, block_cb),
            CyberButton(x + bw + 10, y, bw, h, "CLEAR [C]", Theme.NEON_RED, clear_cb),
            CyberButton(x + (bw + 10) * 2, y, bw, h, "HEAL [E]", Theme.NEON_GREEN, heal_cb),
        ]

    def update(self, mpos, mclick):
        for btn in self.buttons:
            btn.update(mpos, mclick)

    def handle_click(self, mpos):
        for btn in self.buttons:
            if btn.rect.collidepoint(mpos):
                btn.pressed = True
                btn.click_anim = 8
                try: btn.callback()
                except: pass
                return True
        return False

    def draw(self, screen):
        for btn in self.buttons:
            btn.draw(screen)


# ═══════════════════════════════════════════════
#  ADAPTIVE THREAT INDICATOR (#23)
# ═══════════════════════════════════════════════

class AdaptiveThreatIndicator:
    """Shows when AI is adapting to the player's firewall"""
    def __init__(self, w):
        self.w = w
        self.active = False
        self.timer = 0
        self.msg = ""
        self.font = pygame.font.Font(None, 32)
        self.alpha = 0

    def show(self, msg):
        self.msg = f"⚠ THREAT ADAPTING: {msg}"
        self.active = True
        self.timer = 180 # 3 seconds
        self.alpha = 0

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer > 150: self.alpha = min(255, self.alpha + 20)
            elif self.timer < 30: self.alpha = max(0, self.alpha - 10)
            else: self.alpha = 255
        else:
            self.active = False

    def draw(self, screen):
        if not self.active or not self.msg: return
        
        # Center of screen notice
        t = self.font.render(self.msg, True, (255, 100, 0))
        t.set_alpha(self.alpha)
        
        # Glow effect
        p = abs(math.sin(time.time() * 8)) * 100
        glow_color = (255, 100 + int(p), 0)
        
        bg_rect = pygame.Rect(self.w//2 - t.get_width()//2 - 20, 150, t.get_width() + 40, 50)
        s = pygame.Surface((bg_rect.w, bg_rect.h), pygame.SRCALPHA)
        s.fill((40, 10, 0, min(180, self.alpha)))
        screen.blit(s, bg_rect.topleft)
        pygame.draw.rect(screen, (*glow_color, self.alpha), bg_rect, 2, border_radius=8)
        
        screen.blit(t, (self.w//2 - t.get_width()//2, 160))


# ═══════════════════════════════════════════════
#  ACHIEVEMENT NOTIFICATION
# ═══════════════════════════════════════════════

class AchievementNotification:
    """Top-of-screen message bar for achievements"""
    def __init__(self, w):
        self.w = w
        self.msg = ""
        self.timer = 0
        self.font = pygame.font.Font(None, 24)
        self.sub_font = pygame.font.Font(None, 18)
        self.color = Theme.NEON_GREEN
        self.alpha = 0

    def show(self, msg, color=Theme.NEON_GREEN):
        self.msg = msg
        self.color = color
        self.timer = 240 # 4 seconds
        self.alpha = 0

    def update(self):
        if self.timer > 0:
            self.timer -= 1
            if self.timer > 210: # Fade in
                self.alpha = min(255, self.alpha + 15)
            elif self.timer < 30: # Fade out
                self.alpha = max(0, self.alpha - 8)
            else:
                self.alpha = 255
        else:
            self.msg = ""

    def draw(self, screen):
        if self.timer <= 0 or not self.msg: return
        
        # Overlay bar at the very top
        rect = pygame.Rect(self.w//2 - 200, 20, 400, 35)
        bg = pygame.Surface((400, 35), pygame.SRCALPHA)
        bg.fill((0, 20, 10, min(200, self.alpha)))
        screen.blit(bg, rect.topleft)
        
        pygame.draw.rect(screen, (*self.color, self.alpha), rect, 2, border_radius=6)
        
        # Message
        t = self.font.render(self.msg, True, (*self.color, self.alpha))
        screen.blit(t, (rect.centerx - t.get_width()//2, rect.centery - t.get_height()//2))


# ═══════════════════════════════════════════════
#  GAME OVER REPORT (EDUCATIONAL)
# ═══════════════════════════════════════════════

class GameOverReport:
    """Detailed educational report after losing the game"""
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.visible = False
        self.score = 0
        self.failed_reason = ""
        self.advice = []
        self.page = 0  # 0: Reason/Next, 1: Score/Restart
        
        # Increased font sizes for better visibility (#16)
        self.title_font = pygame.font.Font(None, 64)   # was 48
        self.sub_font = pygame.font.Font(None, 42)     # was 32
        self.body_font = pygame.font.Font(None, 32)    # was 24
        self.advice_font = pygame.font.Font(None, 24)  # was 18
        self.footer_font = pygame.font.Font(None, 28)  # new font for footer

    def show(self, score, blocked, leaked):
        self.score = score
        self.blocked = blocked
        self.leaked = leaked
        self.failed_reason = "The network security was breached before all waves could be completed. Critical server components have been compromised."
        self.visible = True
        self.page = 0

    def _wrap_text(self, text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = " ".join(current_line + [word])
            if font.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    def draw(self, screen):
        if not self.visible: return
        
        # Dark dim overlay
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((5, 2, 2, 250)) # Darker background
        screen.blit(ov, (0, 0))
        
        cx = self.w // 2
        mpos = pygame.mouse.get_pos()
        
        if self.page == 0:
            # PAGE 1: NETWORK COMPROMISED + DESCRIPTION
            bw = 700 
            max_content_w = bw - 100
            reason_lines = self._wrap_text(self.failed_reason, self.body_font, max_content_w)
            
            # Box height
            bh = 400
            bx, by = cx - bw//2, self.h//2 - bh//2
            
            # Background Glow
            for i in range(5, 0, -1):
                pygame.draw.rect(screen, (100//i, 0, 0), (bx-i, by-i, bw+i*2, bh+i*2), border_radius=15)
            pygame.draw.rect(screen, (25, 12, 12), (bx, by, bw, bh), border_radius=12)
            pygame.draw.rect(screen, Theme.NEON_RED, (bx, by, bw, bh), 2, border_radius=12)
            
            # Title
            tt = self.title_font.render("NETWORK COMPROMISED", True, Theme.NEON_RED)
            screen.blit(tt, (cx - tt.get_width()//2, by + 40))
            
            pygame.draw.line(screen, (120, 30, 30), (bx + 40, by + 100), (bx + bw - 40, by + 100), 2)
            
            # Failed Reason Header
            rt = self.body_font.render("THREAT ANALYSIS:", True, Theme.NEON_ORANGE)
            screen.blit(rt, (bx + 50, by + 130))
            
            curr_y = by + 175
            for line in reason_lines:
                lt = self.body_font.render(line, True, Theme.TEXT_PRIMARY)
                screen.blit(lt, (bx + 60, curr_y))
                curr_y += 35
                
            # NEXT BUTTON at bottom right
            self.btn_next = pygame.Rect(bx + bw - 150, by + bh - 60, 120, 40)
            nh = self.btn_next.collidepoint(mpos)
            nbg = (0, 70, 90) if nh else (10, 25, 45)
            pygame.draw.rect(screen, nbg, self.btn_next, border_radius=8)
            pygame.draw.rect(screen, Theme.NEON_CYAN, self.btn_next, 2, border_radius=8)
            nt = self.body_font.render("NEXT >>", True, Theme.NEON_CYAN)
            screen.blit(nt, (self.btn_next.centerx - nt.get_width()//2, self.btn_next.centery - nt.get_height()//2))

        else:
            # PAGE 2: SCORES + PLAY AGAIN/QUIT
            bw = 650
            bh = 450
            bx, by = cx - bw//2, self.h//2 - bh//2
            
            # Background Glow
            for i in range(5, 0, -1):
                pygame.draw.rect(screen, (0, 100//i, 100//i), (bx-i, by-i, bw+i*2, bh+i*2), border_radius=15)
            pygame.draw.rect(screen, (12, 20, 25), (bx, by, bw, bh), border_radius=12)
            pygame.draw.rect(screen, Theme.NEON_CYAN, (bx, by, bw, bh), 2, border_radius=12)
            
            # Title
            tt = self.title_font.render("FINAL RESULTS", True, Theme.NEON_CYAN)
            screen.blit(tt, (cx - tt.get_width()//2, by + 30))
            
            # Score details box (inner)
            inner_rect = pygame.Rect(bx + 40, by + 80, bw - 80, 250)
            pygame.draw.rect(screen, (8, 12, 18), inner_rect, border_radius=8)
            pygame.draw.rect(screen, (40, 60, 80), inner_rect, 1, border_radius=8)
            
            st = self.sub_font.render(f"FINAL SCORE: {self.score}", True, Theme.NEON_YELLOW)
            screen.blit(st, (cx - st.get_width()//2, by + 105))
            
            curr_y = by + 160
            at = self.body_font.render("DEFENSE PERFORMANCE:", True, Theme.NEON_GREEN)
            screen.blit(at, (bx + 60, curr_y))
            curr_y += 40
            
            # Show Blocked and Leaked packets
            bt = self.body_font.render(f"Packets Blocked: {self.blocked}", True, Theme.NEON_ORANGE)
            screen.blit(bt, (bx + 80, curr_y))
            curr_y += 35
            
            lt = self.body_font.render(f"Packets Damaging Server: {self.leaked}", True, Theme.NEON_RED)
            screen.blit(lt, (bx + 80, curr_y))
            curr_y += 45
            
            # Failure message
            fail_msg = "Mission Failed: Network compromised before completing all waves."
            ft = self.advice_font.render(fail_msg, True, Theme.TEXT_SECONDARY)
            screen.blit(ft, (cx - ft.get_width()//2, curr_y))
            
            # Footer Buttons (BELOW the box)
            bw_btn = 180
            btn_gap = 40
            btn_y = by + bh + 20 # Below the box
            
            self.btn_replay = pygame.Rect(cx - bw_btn - btn_gap//2, btn_y, bw_btn, 45)
            self.btn_quit = pygame.Rect(cx + btn_gap//2, btn_y, bw_btn, 45)
            
            # Draw Replay Button
            rh = self.btn_replay.collidepoint(mpos)
            rbg = (0, 70, 50) if rh else (15, 35, 25)
            pygame.draw.rect(screen, rbg, self.btn_replay, border_radius=8)
            pygame.draw.rect(screen, Theme.NEON_GREEN, self.btn_replay, 2, border_radius=8)
            rt = self.body_font.render("PLAY AGAIN", True, Theme.NEON_GREEN)
            screen.blit(rt, (self.btn_replay.centerx - rt.get_width()//2, self.btn_replay.centery - rt.get_height()//2))
            
            # Draw Quit Button
            qh = self.btn_quit.collidepoint(mpos)
            qbg = (70, 0, 0) if qh else (35, 15, 15)
            pygame.draw.rect(screen, qbg, self.btn_quit, border_radius=8)
            pygame.draw.rect(screen, Theme.NEON_RED, self.btn_quit, 2, border_radius=8)
            qt = self.body_font.render("QUIT GAME", True, Theme.NEON_RED)
            screen.blit(qt, (self.btn_quit.centerx - qt.get_width()//2, self.btn_quit.centery - qt.get_height()//2))


    def handle_click(self, mpos):
        if not self.visible: return None
        
        if self.page == 0:
            if hasattr(self, 'btn_next') and self.btn_next and self.btn_next.collidepoint(mpos):
                self.page = 1
                return "NEXT_PAGE"
        else:
            if hasattr(self, 'btn_replay') and self.btn_replay and self.btn_replay.collidepoint(mpos):
                self.visible = False
                return "REPLAY"
            if hasattr(self, 'btn_quit') and self.btn_quit and self.btn_quit.collidepoint(mpos):
                return "QUIT"
        return None


# ═══════════════════════════════════════════════
#  SIDEBAR ITEM
# ═══════════════════════════════════════════════

class SidebarItem:
    """Generic item for a sidebar (Attack or Rule)"""
    def __init__(self, x, y, w, h, title, description, color, action_label, action_cb, extra_info="", extra_color=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.title = title
        self.description = description
        self.color = color
        self.action_label = action_label
        self.action_cb = action_cb
        self.extra_info = extra_info
        self.extra_color = extra_color or Theme.NEON_CYAN
        
        self.hovered = False
        self.selected = False
        self.btn_rect = pygame.Rect(x + w - 75, y + 5, 70, 24)
        
        # Slightly larger fonts (#28)
        self.title_font = pygame.font.Font(None, 24)
        self.desc_font = pygame.font.Font(None, 18)
        self.btn_font = pygame.font.Font(None, 17)

    def update(self, mpos):
        self.hovered = self.rect.collidepoint(mpos)

    def handle_click(self, mpos):
        if self.btn_rect.collidepoint(mpos):
            self.action_cb()
            return True
        if self.rect.collidepoint(mpos):
            self.selected = not self.selected
            return True
        return False

    def get_height(self):
        # Accurate height calculation based on font metrics
        h = 55
        # Description height
        words = self.description.split()
        curr = ""
        max_w = self.rect.w - 20
        for w in words:
            test = curr + " " + w if curr else w
            if self.desc_font.size(test)[0] > max_w:
                h += 18
                curr = w
            else:
                curr = test
        if curr: h += 18
        
        # Extra info height
        if self.extra_info:
            h += 10 # Spacer
            words = self.extra_info.split()
            curr = ""
            for w in words:
                test = curr + " " + w if curr else w
                if self.desc_font.size(test)[0] > max_w:
                    h += 18
                    curr = w
                else:
                    curr = test
            if curr: h += 18
            
        return h + 15

    def draw(self, screen, y):
        self.rect.y = y
        self.btn_rect.y = y + 8
        h = self.get_height()
        self.rect.h = h
        
        bg = Theme.PANEL_HOVER if self.hovered else Theme.PANEL_BG
        pygame.draw.rect(screen, bg, self.rect, border_radius=4)
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, 4, h), border_radius=2)
        
        # Title
        tc = Theme.TEXT_BRIGHT if self.hovered else Theme.TEXT_PRIMARY
        screen.blit(self.title_font.render(self.title, True, tc), (self.rect.x + 10, self.rect.y + 12))
        
        # Action Button
        btn_bg = (40, 60, 40) if self.action_label in ["ON", "START"] else (60, 40, 40)
        pygame.draw.rect(screen, btn_bg, self.btn_rect, border_radius=4)
        pygame.draw.rect(screen, self.color, self.btn_rect, 1, border_radius=4)
        bt = self.btn_font.render(self.action_label, True, self.color)
        screen.blit(bt, (self.btn_rect.centerx - bt.get_width()//2, self.btn_rect.centery - bt.get_height()//2))
        
        # Description with proper wrap
        dy = self.rect.y + 42
        words = self.description.split()
        curr = ""
        max_w = self.rect.w - 20
        for w in words:
            test = curr + " " + w if curr else w
            if self.desc_font.size(test)[0] > max_w:
                screen.blit(self.desc_font.render(curr, True, Theme.TEXT_SECONDARY), (self.rect.x + 12, dy))
                dy += 18
                curr = w
            else:
                curr = test
        if curr:
            screen.blit(self.desc_font.render(curr, True, Theme.TEXT_SECONDARY), (self.rect.x + 12, dy))
        
        # Extra info with wrap
        if self.extra_info:
            dy += 22 # Extra spacer
            words = self.extra_info.split()
            curr = ""
            for w in words:
                test = curr + " " + w if curr else w
                if self.desc_font.size(test)[0] > max_w:
                    screen.blit(self.desc_font.render(curr, True, self.extra_color), (self.rect.x + 12, dy))
                    dy += 18
                    curr = w
                else:
                    curr = test
            if curr:
                screen.blit(self.desc_font.render(curr, True, self.extra_color), (self.rect.x + 12, dy))

        return h


# ═══════════════════════════════════════════════
#  SIDEBAR RULE ITEM
# ═══════════════════════════════════════════════

class SidebarRuleItem:
    """Item for firewall sidebar"""
    def __init__(self, x, y, w, rule_id, data, toggle_cb):
        self.rect = pygame.Rect(x, y, w, 40)
        self.rule_id = rule_id
        self.name = data['name']
        self.tier = data['tier']
        self.description = data['description']
        self.enabled = data['enabled']
        self.toggle_cb = toggle_cb
        
        self.hovered = False
        self.selected = False
        self.btn_rect = pygame.Rect(x + w - 65, y + 5, 60, 24)
        
        # Slightly larger fonts (#28)
        self.title_font = pygame.font.Font(None, 24)
        self.desc_font = pygame.font.Font(None, 17)
        self.btn_font = pygame.font.Font(None, 17)

    def update_data(self, d):
        self.enabled = d.get('enabled', False)

    def update(self, mpos):
        self.hovered = self.rect.collidepoint(mpos)

    def handle_click(self, mpos):
        if self.btn_rect.collidepoint(mpos):
            self.toggle_cb(self.rule_id)
            return True
        if self.rect.collidepoint(mpos):
            self.selected = not self.selected
            return True
        return False

    def get_height(self):
        # Accurate height calculation based on font metrics
        words = self.description.split()
        lines = 0
        curr = ""
        max_w = self.rect.w - 20
        for w in words:
            test = curr + " " + w if curr else w
            if self.desc_font.size(test)[0] > max_w:
                lines += 1
                curr = w
            else:
                curr = test
        if curr: lines += 1
        return 60 + lines * 17 + 25

    def draw(self, screen, y):
        self.rect.y = y
        self.btn_rect.y = y + 8
        h = self.get_height()
        self.rect.h = h
        
        tc = Theme.tier_color(self.tier)
        bg = (10, 40, 30) if self.enabled else (Theme.PANEL_HOVER if self.hovered else Theme.PANEL_BG)
        pygame.draw.rect(screen, bg, self.rect, border_radius=4)
        pygame.draw.rect(screen, tc, (self.rect.x, self.rect.y, 4, h), border_radius=2)
        
        # Title
        screen.blit(self.title_font.render(self.name, True, Theme.TEXT_PRIMARY), (self.rect.x + 10, self.rect.y + 12))
        
        # Toggle button
        btn_bg = (0, 80, 40) if self.enabled else (70, 20, 20)
        pygame.draw.rect(screen, btn_bg, self.btn_rect, border_radius=4)
        pygame.draw.rect(screen, (tc if self.enabled else Theme.STATUS_OFF), self.btn_rect, 1, border_radius=4)
        bt = self.btn_font.render("ON" if self.enabled else "OFF", True, Theme.TEXT_BRIGHT)
        screen.blit(bt, (self.btn_rect.centerx - bt.get_width()//2, self.btn_rect.centery - bt.get_height()//2))
        
        # Description with proper wrap
        dy = self.rect.y + 42
        words = self.description.split()
        curr = ""
        max_w = self.rect.w - 20
        for w in words:
            test = curr + " " + w if curr else w
            if self.desc_font.size(test)[0] > max_w:
                screen.blit(self.desc_font.render(curr, True, Theme.NEON_YELLOW), (self.rect.x + 12, dy))
                dy += 17
                curr = w
            else:
                curr = test
        if curr:
            screen.blit(self.desc_font.render(curr, True, Theme.NEON_YELLOW), (self.rect.x + 12, dy))
        
        dy += 6
        st = "Active — defending" if self.enabled else "Inactive — vulnerable"
        sc = Theme.NEON_GREEN if self.enabled else Theme.NEON_RED
        screen.blit(self.desc_font.render(st, True, sc), (self.rect.x + 12, dy))

        return h


# ═══════════════════════════════════════════════
#  FIREWALL SIDEBAR
# ═══════════════════════════════════════════════

class FirewallSidebar:
    """Right sidebar for firewall rules"""
    def __init__(self, x, y, w, h, defense_engine, on_toggle=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.defense = defense_engine
        self.on_toggle = on_toggle
        self.items = []
        self.visible = True
        self.scroll = 0
        
        self.title_font = pygame.font.Font(None, 24)
        self.btn_font = pygame.font.Font(None, 16)
        
        # Enable/Disable All Buttons
        self.btn_all_on = pygame.Rect(x + 5, y + 40, w//2 - 10, 24)
        self.btn_all_off = pygame.Rect(x + w//2 + 5, y + 40, w//2 - 10, 24)
        
        self._build_rules()

    def _build_rules(self):
        self.items = []
        status = self.defense.get_rule_status()
        for rid, data in status.items():
            item = SidebarRuleItem(
                self.rect.x + 5, 0, self.rect.w - 10,
                rid, data, self._toggle
            )
            self.items.append(item)

    def _toggle(self, rid):
        state = self.defense.toggle_rule(rid)
        if self.on_toggle: self.on_toggle(rid, state)
        self._refresh()

    def _refresh(self):
        status = self.defense.get_rule_status()
        for item in self.items:
            d = status.get(item.rule_id, {})
            item.update_data(d)

    def handle_click(self, mpos):
        if not self.visible or not self.rect.collidepoint(mpos): return False
        
        if self.btn_all_on.collidepoint(mpos):
            self.defense.enable_all()
            self._refresh()
            if self.on_toggle: self.on_toggle("ALL", True)
            return True
            
        if self.btn_all_off.collidepoint(mpos):
            self.defense.disable_all()
            self._refresh()
            if self.on_toggle: self.on_toggle("ALL", False)
            return True

        for item in self.items:
            if item.handle_click(mpos):
                return True
        return True

    def update(self, mpos):
        if not self.visible: return
        self._refresh()
        for item in self.items:
            item.update(mpos)

    def handle_scroll(self, dy):
        if not self.visible: return
        self.scroll = max(0, self.scroll - dy * 30)
        # Limit scroll
        total_h = sum(item.get_height() + 5 for item in self.items)
        max_scroll = max(0, total_h - (self.rect.h - 90))
        self.scroll = min(self.scroll, max_scroll)

    def draw(self, screen):
        if not self.visible: return
        
        # Background
        pygame.draw.rect(screen, Theme.PANEL_DARK, self.rect)
        pygame.draw.rect(screen, Theme.NEON_CYAN, self.rect, 1)
        
        # Title
        tt = self.title_font.render("FIREWALL RULES", True, Theme.NEON_CYAN)
        screen.blit(tt, (self.rect.x + self.rect.w//2 - tt.get_width()//2, self.rect.y + 10))
        
        # Enable/Disable All Buttons
        mpos = pygame.mouse.get_pos()
        on_hover = self.btn_all_on.collidepoint(mpos)
        off_hover = self.btn_all_off.collidepoint(mpos)
        
        pygame.draw.rect(screen, (0, 80, 40) if on_hover else (0, 40, 20), self.btn_all_on, border_radius=4)
        pygame.draw.rect(screen, Theme.NEON_GREEN, self.btn_all_on, 1, border_radius=4)
        t_on = self.btn_font.render("ENABLE ALL", True, Theme.NEON_GREEN)
        screen.blit(t_on, (self.btn_all_on.centerx - t_on.get_width()//2, self.btn_all_on.centery - t_on.get_height()//2))
        
        pygame.draw.rect(screen, (80, 20, 20) if off_hover else (40, 10, 10), self.btn_all_off, border_radius=4)
        pygame.draw.rect(screen, Theme.NEON_RED, self.btn_all_off, 1, border_radius=4)
        t_off = self.btn_font.render("DISABLE ALL", True, Theme.NEON_RED)
        screen.blit(t_off, (self.btn_all_off.centerx - t_off.get_width()//2, self.btn_all_off.centery - t_off.get_height()//2))

        pygame.draw.line(screen, Theme.NEON_CYAN, (self.rect.x + 10, self.rect.y + 75), (self.rect.x + self.rect.w - 10, self.rect.y + 75))
        
        # Clip area for scrolling
        clip_rect = pygame.Rect(self.rect.x, self.rect.y + 80, self.rect.w, self.rect.h - 90)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)
        
        # Items
        cy = self.rect.y + 85 - self.scroll
        for item in self.items:
            h = item.draw(screen, cy)
            cy += h + 5
        
        screen.set_clip(old_clip)


# ═══════════════════════════════════════════════
#  ATTACK SIDEBAR
# ═══════════════════════════════════════════════

# ═══════════════════════════════════════════════
#  CONTROL PANEL
# ═══════════════════════════════════════════════

class ControlPanel:
    """Left side panel with toggles and main actions"""
    def __init__(self, x, y, w, h, toggle_auto_cb, toggle_atk_cb, toggle_rule_cb):
        self.rect = pygame.Rect(x, y, w, h)
        self.toggle_auto_cb = toggle_auto_cb
        self.toggle_atk_cb = toggle_atk_cb
        self.toggle_rule_cb = toggle_rule_cb
        
        self.auto_defense = False
        self.title_font = pygame.font.Font(None, 28)
        self.btn_font = pygame.font.Font(None, 22)
        self.desc_font = pygame.font.Font(None, 16)
        
        # Buttons
        bw, bh = w - 40, 45
        self.btn_auto = pygame.Rect(x + 20, y + 60, bw, bh)
        self.btn_atks = pygame.Rect(x + 20, y + 130, bw, bh)
        self.btn_rules = pygame.Rect(x + 20, y + 200, bw, bh)
        
    def handle_click(self, mpos):
        if self.btn_auto.collidepoint(mpos):
            self.auto_defense = not self.auto_defense
            self.toggle_auto_cb(self.auto_defense)
            return True
        if self.btn_atks.collidepoint(mpos):
            self.toggle_atk_cb()
            return True
        if self.btn_rules.collidepoint(mpos):
            self.toggle_rule_cb()
            return True
        return False

    def draw(self, screen):
        # Panel Background
        pygame.draw.rect(screen, Theme.PANEL_DARK, self.rect, border_radius=10)
        pygame.draw.rect(screen, Theme.NEON_BLUE, self.rect, 2, border_radius=10)
        
        # Title
        tt = self.title_font.render("SYSTEM CONTROL", True, Theme.NEON_CYAN)
        screen.blit(tt, (self.rect.centerx - tt.get_width()//2, self.rect.y + 15))
        
        # Auto/Manual Button
        mpos = pygame.mouse.get_pos()
        a_hover = self.btn_auto.collidepoint(mpos)
        a_color = Theme.NEON_GREEN if self.auto_defense else Theme.NEON_YELLOW
        pygame.draw.rect(screen, (20, 30, 40) if a_hover else (10, 15, 25), self.btn_auto, border_radius=5)
        pygame.draw.rect(screen, a_color, self.btn_auto, 2, border_radius=5)
        mode_text = "MODE: AUTO DEFENSE" if self.auto_defense else "MODE: MANUAL"
        at = self.btn_font.render(mode_text, True, a_color)
        screen.blit(at, (self.btn_auto.centerx - at.get_width()//2, self.btn_auto.centery - at.get_height()//2))
        
        # Type of Attack Button
        at_hover = self.btn_atks.collidepoint(mpos)
        pygame.draw.rect(screen, (20, 30, 40) if at_hover else (10, 15, 25), self.btn_atks, border_radius=5)
        pygame.draw.rect(screen, Theme.NEON_ORANGE, self.btn_atks, 2, border_radius=5)
        atk_t = self.btn_font.render("TYPES OF ATTACK", True, Theme.NEON_ORANGE)
        screen.blit(atk_t, (self.btn_atks.centerx - atk_t.get_width()//2, self.btn_atks.centery - atk_t.get_height()//2))
        
        # Rules Button
        r_hover = self.btn_rules.collidepoint(mpos)
        pygame.draw.rect(screen, (20, 30, 40) if r_hover else (10, 15, 25), self.btn_rules, border_radius=5)
        pygame.draw.rect(screen, Theme.NEON_BLUE, self.btn_rules, 2, border_radius=5)
        rules_t = self.btn_font.render("DEFENSE RULES", True, Theme.NEON_BLUE)
        screen.blit(rules_t, (self.btn_rules.centerx - rules_t.get_width()//2, self.btn_rules.centery - rules_t.get_height()//2))

        # Description text
        desc = [
            "Manual: High Resource Usage",
            "Auto: CPU Drain Over Time",
            "",
            "Configure your defenses to",
            "protect the Main Server."
        ]
        y = self.btn_rules.bottom + 30
        for line in desc:
            lt = self.desc_font.render(line, True, Theme.TEXT_SECONDARY)
            screen.blit(lt, (self.rect.x + 20, y))
            y += 18


# ═══════════════════════════════════════════════
#  WAVE PROGRESS BAR
# ═══════════════════════════════════════════════

class WaveProgressBar:
    """Horizontal bar showing wave time remaining"""

    def __init__(self, x, y, w, h):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.progress = 0.0  # 0 to 1
        self.wave_name = ""
        self.wave_num = 0
        self.active = False
        self.font = pygame.font.Font(None, 16)

    def set_wave(self, num, name, progress, active=True):
        self.wave_num = num
        self.wave_name = name
        self.progress = max(0.0, min(1.0, progress))
        self.active = active

    def clear(self):
        self.active = False

    def draw(self, screen):
        if not self.active:
            return

        # Background
        pygame.draw.rect(screen, (15, 20, 30), (self.x, self.y, self.w, self.h), border_radius=4)

        # Fill
        if self.progress < 0.5:
            fc = Theme.NEON_GREEN
        elif self.progress < 0.8:
            fc = Theme.NEON_YELLOW
        else:
            fc = Theme.NEON_RED

        fw = max(0, int(self.w * self.progress))
        if fw > 0:
            pygame.draw.rect(screen, fc, (self.x, self.y, fw, self.h), border_radius=4)

        # Border
        pygame.draw.rect(screen, fc, (self.x, self.y, self.w, self.h), 1, border_radius=4)

        # Text
        pct = int(self.progress * 100)
        txt = f"WAVE {self.wave_num}: {self.wave_name} [{pct}%]"
        t = self.font.render(txt, True, Theme.TEXT_BRIGHT)
        screen.blit(t, (self.x + self.w//2 - t.get_width()//2,
                        self.y + self.h//2 - t.get_height()//2))


# ═══════════════════════════════════════════════
#  LIVE TERMINAL FEED (#16)
# ═══════════════════════════════════════════════

class LiveTerminalFeed:
    """
    Scrolling terminal-style panel showing real attack logs.
    Looks like Snort/Suricata IDS output.
    """

    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.lines = []
        self.max_lines = 60
        self.scroll = 0
        self.font = pygame.font.Font(None, 20) # Smaller font
        self.title_font = pygame.font.Font(None, 22) # Smaller font

    def add_entry(self, text, severity="info"):
        colors = {
            "info": (0, 180, 100),
            "warning": (255, 200, 0),
            "alert": (255, 100, 0),
            "critical": (255, 50, 50),
            "blocked": (0, 255, 150),
        }
        color = colors.get(severity, (0, 180, 100))
        # Pre-render text
        surf = self.font.render(text, True, color)
        self.lines.append({"text": text, "color": color, "surf": surf})
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines:]
        vis = self._vis()
        self.scroll = max(0, len(self.lines) - vis)

    def _vis(self):
        return max(1, (self.rect.h - 40) // 22)

    def clear(self):
        self.lines.clear()
        self.scroll = 0

    def draw(self, screen):
        # Dark terminal background
        pygame.draw.rect(screen, (5, 8, 12), self.rect, border_radius=4)
        pygame.draw.rect(screen, (0, 100, 60), self.rect, 1, border_radius=4)

        # Title bar
        pygame.draw.rect(screen, (0, 40, 25), (self.rect.x, self.rect.y, self.rect.w, 30), border_radius=4)
        self.title_font.set_bold(True)
        tt = self.title_font.render("NETWORK MONITOR", True, (0, 200, 100))
        screen.blit(tt, (self.rect.x + 8, self.rect.y + 4))
        self.title_font.set_bold(False)

        # Scrolling prompt
        dot = ">" if int(time.time() * 2) % 2 == 0 else "_"
        dt = self.font.render(dot, True, (0, 255, 100))
        screen.blit(dt, (self.rect.x + self.rect.w - 18, self.rect.y + 6))

        # Lines
        vis = self._vis()
        end = min(self.scroll + vis, len(self.lines))
        y = self.rect.y + 35
        for i in range(self.scroll, end):
            entry = self.lines[i]
            screen.blit(entry["surf"], (self.rect.x + 8, y))
            y += 22


# ═══════════════════════════════════════════════
#  SMART SUGGESTION BAR (#21)
# ═══════════════════════════════════════════════

class SmartSuggestionBar:
    """Floating suggestion near firewall node"""

    def __init__(self):
        self.tip = ""
        self.timer = 0
        self.font = pygame.font.Font(None, 18)
        self.x = 0
        self.y = 0

    def set_position(self, x, y):
        self.x = x
        self.y = y

    def set_tip(self, tip):
        if tip and tip != self.tip:
            self.tip = tip
            self.timer = 240  # 4 seconds at 60fps

    def update(self):
        if self.timer > 0:
            self.timer -= 1
        else:
            self.tip = ""

    def draw(self, screen):
        if not self.tip or self.timer <= 0:
            return

        alpha = min(255, self.timer * 4)
        t = self.font.render(self.tip, True, Theme.NEON_YELLOW)
        tw = t.get_width() + 16
        th = t.get_height() + 10

        bx = self.x - tw // 2
        by = self.y - 40

        # Background
        bg = pygame.Surface((tw, th), pygame.SRCALPHA)
        bg.fill(safe_rgba((20, 30, 15), min(200, alpha)))
        screen.blit(bg, (bx, by))

        # Border
        pygame.draw.rect(screen, Theme.NEON_YELLOW, (bx, by, tw, th), 1, border_radius=4)

        # Text
        screen.blit(t, (bx + 8, by + 5))

        # Small arrow pointing down
        pygame.draw.polygon(screen, Theme.NEON_YELLOW, [
            (self.x - 5, by + th),
            (self.x + 5, by + th),
            (self.x, by + th + 6)
        ])


# ═══════════════════════════════════════════════
#  MISSION BRIEFING (#11)
# ═══════════════════════════════════════════════

class MissionBriefing:
    """Full-screen briefing before each wave"""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.visible = False
        self.wave_data = None
        self.timer = 0
        self.auto_close = 300  # 5 seconds

        self.title_font = pygame.font.Font(None, 48)
        self.sub_font = pygame.font.Font(None, 28)
        self.body_font = pygame.font.Font(None, 22)
        self.hint_font = pygame.font.Font(None, 20)
        self.btn_font = pygame.font.Font(None, 24)

        self.btn_ready = pygame.Rect(width//2 - 80, height - 120, 160, 40)

    def show(self, wave_data):
        self.wave_data = wave_data
        self.visible = True
        self.timer = 0

    def handle_click(self, mpos):
        if not self.visible:
            return False
        if self.btn_ready.collidepoint(mpos):
            self.visible = False
            return True
        return False

    def handle_key(self, key):
        if not self.visible:
            return False
        if key in [pygame.K_RETURN, pygame.K_SPACE]:
            self.visible = False
            return True
        return False

    def update(self):
        if not self.visible:
            return
        self.timer += 1

    def draw(self, screen):
        if not self.visible or not self.wave_data:
            return

        w = self.wave_data

        # Dim overlay
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((0, 5, 15, 235)) # Slightly darker
        screen.blit(ov, (0, 0))

        cx = self.w // 2

        # Title
        tt = self.title_font.render(f"WAVE {w.get('num', '?')}", True, Theme.NEON_PURPLE)
        screen.blit(tt, (cx - tt.get_width()//2, 80))

        nt = self.sub_font.render(w.get('name', '').upper(), True, Theme.NEON_CYAN)
        screen.blit(nt, (cx - nt.get_width()//2, 135))

        # Divider
        pygame.draw.line(screen, Theme.NEON_PURPLE, (cx-200, 170), (cx+200, 170), 2)

        # Expected attacks
        y = 190
        at = self.body_font.render("INCOMING ATTACKS:", True, Theme.NEON_RED)
        screen.blit(at, (cx - at.get_width()//2, y))
        y += 35

        attacks = w.get('attacks', [])
        try:
            from firewall import AttackDatabase
            for aid in attacks:
                info = AttackDatabase.get(aid)
                if info:
                    name = info.get('name', aid)
                    sev = info.get('severity', '?')
                    dmg = info.get('damage', 0)
                    sc = Theme.severity_color(sev)

                    row = f"  {name}  |  {sev}  |  {dmg} DMG"
                    rt = self.body_font.render(row, True, sc)
                    screen.blit(rt, (cx - rt.get_width()//2, y))
                    y += 28
        except:
            for aid in attacks:
                rt = self.body_font.render(f"  {aid}", True, Theme.NEON_RED)
                screen.blit(rt, (cx - rt.get_width()//2, y))
                y += 28

        # Strategy/Hint with word-wrap
        y += 30
        hint = w.get('hint', '')
        if hint:
            ht_label = self.hint_font.render("STRATEGY:", True, Theme.NEON_YELLOW)
            screen.blit(ht_label, (cx - ht_label.get_width()//2, y))
            y += 22
            
            # Simple word wrap for hint
            words = hint.split()
            max_w = 600
            curr_line = []
            for word in words:
                test = " ".join(curr_line + [word])
                if self.hint_font.size(test)[0] < max_w:
                    curr_line.append(word)
                else:
                    line_surf = self.hint_font.render(" ".join(curr_line), True, Theme.TEXT_PRIMARY)
                    screen.blit(line_surf, (cx - line_surf.get_width()//2, y))
                    y += 20
                    curr_line = [word]
            if curr_line:
                line_surf = self.hint_font.render(" ".join(curr_line), True, Theme.TEXT_PRIMARY)
                screen.blit(line_surf, (cx - line_surf.get_width()//2, y))
                y += 20

        # Duration
        y += 25
        dur = w.get('duration', 0)
        dt = self.hint_font.render(f"Mission Duration: {dur} seconds", True, Theme.TEXT_SECONDARY)
        screen.blit(dt, (cx - dt.get_width()//2, y))

        # Ready button
        mpos = pygame.mouse.get_pos()
        hover = self.btn_ready.collidepoint(mpos)
        bg = (0, 70, 50) if hover else (15, 35, 25)
        pygame.draw.rect(screen, bg, self.btn_ready, border_radius=8)
        pygame.draw.rect(screen, Theme.NEON_GREEN, self.btn_ready, 2, border_radius=8)
        bt = self.btn_font.render("DEPLOY NOW", True, Theme.NEON_GREEN)
        screen.blit(bt, (self.btn_ready.centerx - bt.get_width()//2,
                         self.btn_ready.centery - bt.get_height()//2))

        # Auto-close countdown
        remain = max(0, (self.auto_close - self.timer) // 60)
        ct = self.hint_font.render(f"System auto-deploy in {remain}s...", True, Theme.TEXT_DIM)
        screen.blit(ct, (cx - ct.get_width()//2, self.h - 60))


# ═══════════════════════════════════════════════
#  POST-WAVE REPORT (#12)
# ═══════════════════════════════════════════════

class PostWaveReport:
    """Summary after each wave"""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.visible = False
        self.data = {}
        self.timer = 0
        self.duration = 240  # 4 seconds

        # Increased font sizes (#28)
        self.title_font = pygame.font.Font(None, 48) # was 40
        self.stat_font = pygame.font.Font(None, 28)  # was 24
        self.val_font = pygame.font.Font(None, 30)   # was 26

    def show(self, data):
        self.data = data
        self.visible = True
        self.timer = 0

    def update(self):
        if self.visible:
            self.timer += 1

    def handle_click(self, mpos):
        if self.visible:
            self.visible = False
            return True
        return False

    def draw(self, screen):
        if not self.visible:
            return

        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((0, 10, 5, 220))
        screen.blit(ov, (0, 0))

        cx = self.w // 2

        # Box - Wider (#28)
        bw, bh = 450, 320
        bx, by = cx - bw//2, self.h//2 - bh//2
        pygame.draw.rect(screen, (10, 20, 15), (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(screen, Theme.NEON_GREEN, (bx, by, bw, bh), 2, border_radius=10)

        # Title
        wn = self.data.get('wave_num', '?')
        tt = self.title_font.render(f"WAVE {wn} COMPLETE", True, Theme.NEON_GREEN)
        screen.blit(tt, (cx - tt.get_width()//2, by + 20))

        pygame.draw.line(screen, Theme.NEON_GREEN, (bx+30, by+65), (bx+bw-30, by+65), 1)

        # Stats
        y = by + 85
        stats = [
            ("Damage Taken", f"-{self.data.get('damage_taken', 0)} HP", Theme.NEON_RED),
            ("Packets Blocked", str(self.data.get('blocked', 0)), Theme.NEON_ORANGE),
            ("Intel Collected", str(self.data.get('intel', 0)), Theme.NEON_CYAN),
            ("Rules Active", str(self.data.get('rules_active', 0)), Theme.NEON_CYAN),
            ("Wave Score", f"+{self.data.get('wave_score', 0)}", Theme.NEON_GREEN),
        ]
        for label, val, color in stats:
            lt = self.stat_font.render(label, True, Theme.TEXT_SECONDARY)
            screen.blit(lt, (bx + 40, y))
            vt = self.val_font.render(val, True, color)
            screen.blit(vt, (bx + bw - vt.get_width() - 40, y))
            y += 40

        # Best rule
        best = self.data.get('best_rule', '')
        if best:
            y += 5
            bt = self.stat_font.render(f"MVP Rule: {best}", True, Theme.NEON_YELLOW)
            screen.blit(bt, (cx - bt.get_width()//2, y))

        # Click to continue
        ct = self.stat_font.render("Click to continue...", True, Theme.TEXT_DIM)
        screen.blit(ct, (cx - ct.get_width()//2, by + bh - 35))


# ═══════════════════════════════════════════════
#  VICTORY REPORT (#12 - Success)
# ═══════════════════════════════════════════════

class VictoryReport:
    """Final summary after winning the game - Two Page Version"""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.visible = False
        self.data = {}
        self.pulse = 0.0
        self.page = 0 # 0: Completion Message, 1: Final Score

        self.title_font = pygame.font.Font(None, 72)
        self.sub_font = pygame.font.Font(None, 42)
        self.stat_font = pygame.font.Font(None, 28)
        self.val_font = pygame.font.Font(None, 32)
        self.body_font = pygame.font.Font(None, 24)
        
        # Buttons
        self.btn_next = pygame.Rect(width//2 - 75, height - 150, 150, 45)
        self.btn_replay = pygame.Rect(width//2 - 190, height - 150, 150, 45)
        self.btn_quit = pygame.Rect(width//2 + 40, height - 150, 150, 45)

    def show(self, score, high_score, blocked, leaked, intel):
        self.data = {
            "score": score,
            "high_score": high_score,
            "blocked": blocked,
            "leaked": leaked,
            "intel": intel,
            "is_new_high": score >= high_score and score > 0
        }
        self.visible = True
        self.pulse = 0.0
        self.page = 0

    def update(self):
        if self.visible:
            self.pulse = (self.pulse + 0.05) % (2 * math.pi)

    def handle_click(self, mpos):
        if not self.visible: return None
        
        if self.page == 0:
            if self.btn_next.collidepoint(mpos):
                self.page = 1
                return "NEXT"
        else:
            if self.btn_replay.collidepoint(mpos):
                self.visible = False
                return "RESET"
            if self.btn_quit.collidepoint(mpos):
                return "QUIT"
        return None

    def draw(self, screen):
        if not self.visible:
            return

        # Dim overlay (Greenish tint)
        ov = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        ov.fill((0, 15, 10, 245))
        screen.blit(ov, (0, 0))

        cx = self.w // 2
        mpos = pygame.mouse.get_pos()
        p = abs(math.sin(self.pulse))
        
        if self.page == 0:
            # PAGE 0: COMPLETION MESSAGE
            tc = safe_color(0, 200 + 55*p, 100 + 100*p)
            tt = self.title_font.render("WAVES CLEARED!", True, tc)
            screen.blit(tt, (cx - tt.get_width()//2, 200))

            st = self.sub_font.render("All three security waves have been neutralized.", True, Theme.TEXT_PRIMARY)
            screen.blit(st, (cx - st.get_width()//2, 280))
            
            # Next Button
            nh = self.btn_next.collidepoint(mpos)
            nbg = (0, 80, 60) if nh else (0, 40, 30)
            pygame.draw.rect(screen, nbg, self.btn_next, border_radius=8)
            pygame.draw.rect(screen, Theme.NEON_GREEN, self.btn_next, 2, border_radius=8)
            nt = self.stat_font.render("NEXT", True, Theme.NEON_GREEN)
            screen.blit(nt, (self.btn_next.centerx - nt.get_width()//2, self.btn_next.centery - nt.get_height()//2))

        else:
            # PAGE 1: FINAL SCORE
            tc = safe_color(0, 255, 150)
            tt = self.title_font.render("FINAL SECURITY AUDIT", True, tc)
            screen.blit(tt, (cx - tt.get_width()//2, 80))

            # Box
            bw, bh = 550, 360
            bx, by = cx - bw//2, 160
            pygame.draw.rect(screen, (10, 25, 20), (bx, by, bw, bh), border_radius=15)
            pygame.draw.rect(screen, Theme.NEON_GREEN, (bx, by, bw, bh), 2, border_radius=15)

            stats = [
                ("Total Score", str(self.data.get('score', 0)), Theme.NEON_YELLOW),
                ("Packets Blocked", str(self.data.get('blocked', 0)), Theme.NEON_GREEN),
                ("Packets Leaked", str(self.data.get('leaked', 0)), Theme.NEON_RED),
                ("High Score", str(max(self.data.get('score', 0), self.data.get('high_score', 0))), Theme.NEON_CYAN),
            ]

            y = by + 40
            for label, val, color in stats:
                lt = self.stat_font.render(label, True, Theme.TEXT_PRIMARY)
                screen.blit(lt, (bx + 60, y))
                vt = self.val_font.render(val, True, color)
                screen.blit(vt, (bx + bw - vt.get_width() - 60, y))
                y += 50

            # New High Score Notification
            if self.data.get('is_new_high'):
                nst = self.sub_font.render("★ NEW HIGH SCORE ★", True, Theme.NEON_YELLOW)
                screen.blit(nst, (cx - nst.get_width()//2, y + 20))

            # Buttons
            # Play Again
            rh = self.btn_replay.collidepoint(mpos)
            rbg = (0, 80, 40) if rh else (0, 40, 20)
            pygame.draw.rect(screen, rbg, self.btn_replay, border_radius=8)
            pygame.draw.rect(screen, Theme.NEON_GREEN, self.btn_replay, 2, border_radius=8)
            rt = self.stat_font.render("PLAY AGAIN", True, Theme.NEON_GREEN)
            screen.blit(rt, (self.btn_replay.centerx - rt.get_width()//2, self.btn_replay.centery - rt.get_height()//2))

            # Quit
            qh = self.btn_quit.collidepoint(mpos)
            qbg = (80, 0, 0) if qh else (40, 0, 0)
            pygame.draw.rect(screen, qbg, self.btn_quit, border_radius=8)
            pygame.draw.rect(screen, Theme.NEON_RED, self.btn_quit, 2, border_radius=8)
            qt = self.stat_font.render("QUIT", True, Theme.NEON_RED)
            screen.blit(qt, (self.btn_quit.centerx - qt.get_width()//2, self.btn_quit.centery - qt.get_height()//2))


class AttackEncyclopedia:
    """
    Grid view of attacks. Selecting one shows details.
    Game pauses while open.
    """
    STATE_GRID = 0
    STATE_DETAIL = 1

    def __init__(self, width, height):
        self.w, self.h = width, height
        self.visible = False
        self.state = self.STATE_GRID
        self.selected_atk = None
        self.attacks = []
        
        self.title_font = pygame.font.Font(None, 42)
        self.name_font = pygame.font.Font(None, 32)
        self.body_font = pygame.font.Font(None, 22)
        self.label_font = pygame.font.Font(None, 20)
        
        self.close_rect = pygame.Rect(width - 60, 20, 40, 40)
        self.grid_rects = {} # aid -> Rect
        
        self._load_attacks()

    def _load_attacks(self):
        try:
            from firewall import AttackDatabase
            self.attacks = []
            for aid in AttackDatabase.all_ids():
                info = AttackDatabase.get(aid)
                if info:
                    self.attacks.append({"id": aid, **info})
        except: pass

    def toggle(self):
        self.visible = not self.visible
        if self.visible:
            self.state = self.STATE_GRID
            self._load_attacks()

    def show(self): self.visible = True; self.state = self.STATE_GRID; self._load_attacks()
    def hide(self): self.visible = False

    def handle_click(self, mpos):
        if not self.visible: return False
        
        # Close/Back button logic
        if self.close_rect.collidepoint(mpos):
            if self.state == self.STATE_DETAIL:
                self.state = self.STATE_GRID
            else:
                self.visible = False
            return True
            
        if self.state == self.STATE_GRID:
            for aid, rect in self.grid_rects.items():
                if rect.collidepoint(mpos):
                    self.selected_atk = next(a for a in self.attacks if a['id'] == aid)
                    self.state = self.STATE_DETAIL
                    return True
        elif self.state == self.STATE_DETAIL:
            # Maybe clicking background of detail goes back?
            # For now just return True to consume the click
            return True
            
        return False

    def handle_key(self, key):
        if not self.visible: return False
        if key == pygame.K_ESCAPE or key == pygame.K_i:
            if self.state == self.STATE_DETAIL:
                self.state = self.STATE_GRID
            else:
                self.visible = False
            return True
        return False

    def draw(self, screen):
        if not self.visible: return
        
        # Dark overlay
        overlay = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
        overlay.fill((5, 10, 20, 245))
        screen.blit(overlay, (0, 0))
        
        # Close Button
        pygame.draw.rect(screen, Theme.NEON_RED, self.close_rect, 2, border_radius=5)
        ct = self.body_font.render("X", True, Theme.NEON_RED)
        screen.blit(ct, (self.close_rect.centerx - ct.get_width()//2, self.close_rect.centery - ct.get_height()//2))

        if self.state == self.STATE_GRID:
            self._draw_grid(screen)
        else:
            self._draw_detail(screen)

    def _draw_grid(self, screen):
        tt = self.title_font.render("SELECT THREAT TYPE", True, Theme.NEON_ORANGE)
        screen.blit(tt, (self.w//2 - tt.get_width()//2, 50))
        
        # Draw rectangular boxes for each attack
        cols = 3
        margin = 40
        start_y = 120
        bw = (self.w - (cols+1)*margin) // cols
        bh = 80
        
        self.grid_rects = {}
        mpos = pygame.mouse.get_pos()
        
        for i, atk in enumerate(self.attacks):
            row = i // cols
            col = i % cols
            bx = margin + col * (bw + margin)
            by = start_y + row * (bh + margin)
            rect = pygame.Rect(bx, by, bw, bh)
            self.grid_rects[atk['id']] = rect
            
            hover = rect.collidepoint(mpos)
            pygame.draw.rect(screen, (30, 45, 70) if hover else (15, 25, 45), rect, border_radius=10)
            pygame.draw.rect(screen, atk['color'], rect, 2, border_radius=10)
            
            name = self.name_font.render(atk['name'], True, Theme.TEXT_BRIGHT)
            screen.blit(name, (rect.centerx - name.get_width()//2, rect.centery - name.get_height()//2))

    def _draw_detail(self, screen):
        atk = self.selected_atk
        if not atk: return
        
        # Detail Container
        rect = pygame.Rect(100, 80, self.w - 200, self.h - 200)
        pygame.draw.rect(screen, (20, 30, 50), rect, border_radius=15)
        pygame.draw.rect(screen, atk['color'], rect, 3, border_radius=15)
        
        # Name and Severity
        name = self.title_font.render(atk['name'], True, atk['color'])
        screen.blit(name, (rect.x + 40, rect.y + 40))
        
        sev_color = Theme.severity_color(atk['severity'])
        sev = self.name_font.render(f"SEVERITY: {atk['severity']}", True, sev_color)
        screen.blit(sev, (rect.right - sev.get_width() - 40, rect.y + 40))
        
        # Protocol
        prot = self.body_font.render(f"PROTOCOL: {atk.get('protocol', 'TCP/UDP')}", True, Theme.NEON_CYAN)
        screen.blit(prot, (rect.x + 40, rect.y + 85))
        
        # Description
        desc_title = self.name_font.render("DEFINITION", True, Theme.TEXT_SECONDARY)
        screen.blit(desc_title, (rect.x + 40, rect.y + 130))
        
        words = atk['explanation'].split(' ')
        lines = []
        curr_line = ""
        for w in words:
            if self.body_font.size(curr_line + w)[0] < rect.w - 100:
                curr_line += w + " "
            else:
                lines.append(curr_line)
                curr_line = w + " "
        lines.append(curr_line)
        
        y = rect.y + 165
        for line in lines:
            lt = self.body_font.render(line, True, Theme.TEXT_PRIMARY)
            screen.blit(lt, (rect.x + 40, y))
            y += 24
            
        # Rules to counter
        rule_title = self.name_font.render("RECOMMENDED COUNTERMEASURES", True, Theme.NEON_GREEN)
        screen.blit(rule_title, (rect.x + 40, y + 20))
        
        counters = atk.get('countered_by', [])
        y += 55
        if not counters:
            screen.blit(self.body_font.render("No specific rules — use manual intervention.", True, Theme.TEXT_DIM), (rect.x + 40, y))
        else:
            from firewall import DefenseEngine
            for rid in counters:
                rule_name = DefenseEngine.RULE_DEFS.get(rid, {}).get('name', rid)
                rt = self.body_font.render(f"• {rule_name}", True, Theme.NEON_BLUE)
                screen.blit(rt, (rect.x + 40, y))
                y += 24
        
        # Back Prompt
        bt = self.label_font.render("Press 'X' or ESC to return to grid", True, Theme.TEXT_DIM)
        screen.blit(bt, (rect.centerx - bt.get_width()//2, rect.bottom - 30))


# ═══════════════════════════════════════════════
#  FIREWALL RULE ROW (readable)
# ═══════════════════════════════════════════════

class FirewallRuleRow:
    ROW_H = 40

    def __init__(self, x, y, w, rule_id, data, toggle_cb):
        self.x, self.y, self.w = x, y, w
        self.rule_id = rule_id
        self.name = data.get("name", "?")
        self.tier = data.get("tier", 1)
        self.desc = data.get("description", "")
        self.eff = data.get("effectiveness", 0.0)
        self.enabled = data.get("enabled", False)
        self.count = data.get("count", 0)
        self.toggle_cb = toggle_cb

        self.rect = pygame.Rect(x, y, w, self.ROW_H)
        self.btn_rect = pygame.Rect(x + w - 55, y + 8, 45, 24)
        
        self.fn = pygame.font.Font(None, 18)
        self.fs = pygame.font.Font(None, 14)

    def update_data(self, d):
        self.enabled = d.get("enabled", False)
        self.count = d.get("count", 0)

    def update_pos(self, x, y):
        self.x, self.y = x, y
        self.rect.topleft = (x, y)
        self.btn_rect.topleft = (x + self.w - 55, y + 8)

    def handle_click(self, mpos):
        if self.rect.collidepoint(mpos):
            self.toggle_cb(self.rule_id)
            return True
        return False

    def draw(self, screen):
        mpos = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mpos)
        
        # Row Background
        bg = (30, 40, 60) if hover else (20, 25, 40)
        pygame.draw.rect(screen, bg, self.rect, border_radius=4)
        
        # Tier indicator
        t_color = Theme.tier_color(self.tier)
        pygame.draw.rect(screen, t_color, (self.x + 5, self.y + 10, 4, 20), border_radius=2)
        
        # Name
        name_t = self.fn.render(self.name, True, Theme.TEXT_BRIGHT)
        screen.blit(name_t, (self.x + 15, self.y + 12))
        
        # Status Button
        b_color = Theme.STATUS_ON if self.enabled else Theme.STATUS_OFF
        pygame.draw.rect(screen, b_color, self.btn_rect, border_radius=4)
        st = "ON" if self.enabled else "OFF"
        st_t = self.fn.render(st, True, (0, 0, 0) if self.enabled else Theme.TEXT_BRIGHT)
        screen.blit(st_t, (self.btn_rect.centerx - st_t.get_width()//2, self.btn_rect.centery - st_t.get_height()//2))

        # Tooltip for description if hovered
        if hover:
            return self.desc
        return None

# ═══════════════════════════════════════════════
#  DEFENSE PANEL (All rules on one page)
# ═══════════════════════════════════════════════

class DefensePanel:
    """
    Shows all 24+ rules in two columns with scrolling.
    Pauses game while visible.
    """

    def __init__(self, x, y, w, h, defense_engine, on_toggle=None):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.defense = defense_engine
        self.on_toggle = on_toggle
        self.visible = False
        self.rows = []
        self.scroll = 0

        self.title_font = pygame.font.Font(None, 32)
        self.header_font = pygame.font.Font(None, 24)
        self.tip_font = pygame.font.Font(None, 18)

        # Larger close button for better hit detection
        self.close_rect = pygame.Rect(x + w - 55, y + 10, 45, 45)
        self.btn_enable_all = pygame.Rect(x + 20, y + h - 45, 120, 35)
        self.btn_disable_all = pygame.Rect(x + 150, y + h - 45, 120, 35)

        self._build_panel()

    def _build_panel(self):
        self.rows = []
        status = self.defense.get_rule_status()
        all_rules = self.defense.get_all_rules()
        
        # Split into Firewall (Tiers 1-4) and Server (Tiers 5-7)
        fw_rules = sorted([r for r in all_rules if r.tier <= 4], key=lambda x: x.tier)
        srv_rules = sorted([r for r in all_rules if r.tier > 4], key=lambda x: x.tier)
        
        # Column width
        col_w = (self.w - 80) // 2
        
        # Left Column (Firewall)
        cx = self.x + 30
        cy = 0
        for r in fw_rules:
            row = FirewallRuleRow(cx, cy, col_w, r.rule_id, status.get(r.rule_id, {}), self._toggle)
            self.rows.append(row)
            cy += row.ROW_H + 5
            
        # Right Column (Server)
        cx = self.x + col_w + 50
        cy = 0
        for r in srv_rules:
            row = FirewallRuleRow(cx, cy, col_w, r.rule_id, status.get(r.rule_id, {}), self._toggle)
            self.rows.append(row)
            cy += row.ROW_H + 5

    def _toggle(self, rid):
        state = self.defense.toggle_rule(rid)
        if self.on_toggle: self.on_toggle(rid, state)
        self._refresh()

    def _refresh(self):
        status = self.defense.get_rule_status()
        for row in self.rows:
            row.update_data(status.get(row.rule_id, {}))

    def toggle(self):
        self.visible = not self.visible
        if self.visible: 
            self._build_panel()
            self.scroll = 0

    def toggle_visible(self):
        self.toggle()

    def show(self): 
        self.visible = True
        self._build_panel()
        self.scroll = 0

    def hide(self): self.visible = False

    def handle_scroll(self, dy):
        if not self.visible: return
        self.scroll = max(0, self.scroll - dy * 25)
        # Calculate max scroll
        max_h = 0
        if self.rows:
            cols = {}
            for r in self.rows: cols[r.x] = max(cols.get(r.x, 0), r.y + r.ROW_H)
            max_h = max(cols.values()) if cols else 0
        
        max_scroll = max(0, max_h - (self.h - 150))
        self.scroll = min(self.scroll, max_scroll)

    def handle_click(self, mpos):
        if not self.visible: return False
        
        if self.close_rect.collidepoint(mpos):
            self.hide(); return True
            
        if self.btn_enable_all.collidepoint(mpos):
            self.defense.enable_all(); self._refresh(); return True
            
        if self.btn_disable_all.collidepoint(mpos):
            self.defense.disable_all(); self._refresh(); return True
            
        for row in self.rows:
            # The row's y is already relative to the clip area (start_y=80)
            ry_on_screen = self.y + 80 + row.y - self.scroll
            # Check horizontal bounds
            if row.x <= mpos[0] <= row.x + row.w:
                # Check vertical bounds relative to screen and clip area
                if ry_on_screen <= mpos[1] <= ry_on_screen + row.ROW_H:
                    if self.y + 80 <= mpos[1] <= self.y + self.h - 60:
                        self._toggle(row.rule_id)
                        return True
        return False

    def update(self, mpos):
        if not self.visible: return
        self._refresh()

    def draw(self, screen):
        if not self.visible: return
        
        # Background Overlay
        ov = pygame.Surface((1200, 700), pygame.SRCALPHA)
        ov.fill((10, 15, 30, 245))
        screen.blit(ov, (0, 0))
        
        # Panel
        pygame.draw.rect(screen, (15, 22, 35), (self.x, self.y, self.w, self.h), border_radius=15)
        pygame.draw.rect(screen, Theme.NEON_BLUE, (self.x, self.y, self.w, self.h), 2, border_radius=15)
        
        # Title
        tt = self.title_font.render("NETWORK DEFENSE CONFIGURATION", True, Theme.NEON_CYAN)
        screen.blit(tt, (self.x + self.w//2 - tt.get_width()//2, self.y + 15))
        
        # Close Button
        mpos = pygame.mouse.get_pos()
        c_hover = self.close_rect.collidepoint(mpos)
        pygame.draw.rect(screen, (60, 20, 20) if c_hover else (30, 10, 10), self.close_rect, border_radius=8)
        pygame.draw.rect(screen, Theme.NEON_RED, self.close_rect, 2, border_radius=8)
        xt = self.header_font.render("X", True, Theme.NEON_RED)
        screen.blit(xt, (self.close_rect.centerx - xt.get_width()//2, self.close_rect.centery - xt.get_height()//2))

        # Column Headers
        h1 = self.header_font.render("FIREWALL RULES", True, Theme.NEON_ORANGE)
        screen.blit(h1, (self.x + 30, self.y + 55))
        h2 = self.header_font.render("SERVER CONFIGURATION", True, Theme.NEON_GREEN)
        screen.blit(h2, (self.x + self.w//2 + 20, self.y + 55))

        # Clip area for rows
        clip_rect = pygame.Rect(self.x, self.y + 80, self.w, self.h - 140)
        old_clip = screen.get_clip()
        screen.set_clip(clip_rect)

        # Draw Rows
        hover_desc = None
        for row in self.rows:
            ry = self.y + 80 + row.y - self.scroll
            if ry + row.ROW_H > self.y + 80 and ry < self.y + self.h - 60:
                old_row_y = row.y
                row.y = ry
                row.rect.y = ry
                row.btn_rect.y = ry + 8
                desc = row.draw(screen)
                if desc: hover_desc = desc
                row.y = old_row_y
            
        screen.set_clip(old_clip)
            
        # Draw Enable/Disable buttons
        for btn, label, color in [(self.btn_enable_all, "ENABLE ALL", Theme.NEON_GREEN), 
                                 (self.btn_disable_all, "DISABLE ALL", Theme.NEON_RED)]:
            hover = btn.collidepoint(mpos)
            pygame.draw.rect(screen, (25, 40, 35) if hover else (15, 20, 25), btn, border_radius=6)
            pygame.draw.rect(screen, color, btn, 2, border_radius=6)
            bt = self.tip_font.render(label, True, color)
            screen.blit(bt, (btn.centerx - bt.get_width()//2, btn.centery - bt.get_height()//2))

        # Scrollbar
        scrollbar_h = self.h - 140
        pygame.draw.rect(screen, (30, 40, 50), (self.x + self.w - 10, self.y + 80, 6, scrollbar_h), border_radius=3)
        max_h = 0
        if self.rows:
            cols = {}
            for r in self.rows: cols[r.x] = max(cols.get(r.x, 0), r.y + r.ROW_H)
            max_h = max(cols.values()) if cols else 1
        handle_h = max(20, (scrollbar_h / max(1, max_h)) * scrollbar_h)
        handle_y = self.y + 80 + (self.scroll / max(1, max_h)) * scrollbar_h
        pygame.draw.rect(screen, Theme.NEON_BLUE, (self.x + self.w - 10, min(self.y+80+scrollbar_h-handle_h, handle_y), 6, handle_h), border_radius=3)

        if hover_desc:
            self._draw_tooltip(screen, hover_desc, mpos)

    def _draw_tooltip(self, screen, text, mpos):
        # Draw a small box with description near mouse
        words = text.split(' ')
        lines = []
        curr = ""
        for w in words:
            if self.tip_font.size(curr + w)[0] < 250:
                curr += w + " "
            else:
                lines.append(curr)
                curr = w + " "
        lines.append(curr)
        
        tw = 260
        th = len(lines) * 18 + 10
        tx, ty = mpos[0] + 20, mpos[1] + 20
        if tx + tw > 1200: tx = mpos[0] - tw - 20
        if ty + th > 700: ty = mpos[1] - th - 20
        
        pygame.draw.rect(screen, (10, 15, 25), (tx, ty, tw, th), border_radius=5)
        pygame.draw.rect(screen, Theme.NEON_YELLOW, (tx, ty, tw, th), 1, border_radius=5)
        
        for i, line in enumerate(lines):
            lt = self.tip_font.render(line, True, Theme.TEXT_PRIMARY)
            screen.blit(lt, (tx + 5, ty + 5 + i * 18))



# ═══════════════════════════════════════════════
#  ATTACK POPUP (hover)
# ═══════════════════════════════════════════════

class AttackPopup:
    def __init__(self, defense_engine):
        self.defense = defense_engine
        self.visible = False
        self.attack_id = None
        self.source_ip = None
        self.px = self.py = 0
        self.W, self.H = 310, 210
        self.ft = pygame.font.Font(None, 18)
        self.fb = pygame.font.Font(None, 15)
        self.fs = pygame.font.Font(None, 16)

    def show(self, aid, ip, mx, my):
        self.visible = True; self.attack_id = aid; self.source_ip = ip
        self.px = mx + 15; self.py = my - 10

    def hide(self): self.visible = False

    def draw(self, screen):
        if not self.visible or not self.attack_id: return
        try:
            from firewall import AttackDatabase
            info = AttackDatabase.get(self.attack_id)
        except: return
        if not info: return

        sw, sh = screen.get_size()
        if self.px + self.W > sw: self.px = sw - self.W - 10
        if self.py + self.H > sh: self.py = sh - self.H - 10

        rect = pygame.Rect(self.px, self.py, self.W, self.H)
        pygame.draw.rect(screen, (8,14,25), rect, border_radius=6)
        sc = Theme.severity_color(info.get("severity", "LOW"))
        pygame.draw.rect(screen, sc, rect, 2, border_radius=6)
        pygame.draw.rect(screen, sc, (self.px, self.py, 4, self.H), border_radius=2)

        y = self.py + 8
        screen.blit(self.ft.render(f"! {info.get('name','?')} [{info.get('severity','?')}]", True, sc), (self.px+10, y)); y += 18
        if self.source_ip:
            screen.blit(self.fb.render(f"From: {self.source_ip}", True, Theme.TEXT_SECONDARY), (self.px+10, y)); y += 14
        screen.blit(self.fb.render(f"Damage: {info.get('damage',0)} HP", True, Theme.NEON_RED), (self.px+10, y)); y += 16

        exp = info.get("explanation", "")
        lc = 48
        lines = [exp[i:i+lc] for i in range(0, len(exp), lc)]
        for line in lines[:4]:
            screen.blit(self.fb.render(line, True, Theme.TEXT_PRIMARY), (self.px+10, y)); y += 13
        y += 4

        counters = info.get("countered_by", [])
        for cid in counters[:2]:
            rule = self.defense.get_rule(cid)
            if rule:
                if rule.enabled:
                    screen.blit(self.fs.render(f">> {rule.name}: ON", True, Theme.NEON_GREEN), (self.px+10, y))
                else:
                    screen.blit(self.fs.render(f"X {rule.name}: OFF", True, Theme.NEON_RED), (self.px+10, y))
                y += 16


# ═══════════════════════════════════════════════
#  DEFENSE BAR (compact)
# ═══════════════════════════════════════════════

class DefenseBar:
    def __init__(self, x, y, w, h, on_click=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.on_click = on_click
        self.active = self.total = self.coverage = 0
        self.hovered = False
        self.font = pygame.font.Font(None, 16)
        self.fs = pygame.font.Font(None, 13)

    def update(self, defense, mpos):
        try:
            s = defense.get_stats()
            self.active = s.get('active_rules', 0)
            self.total = s.get('total_rules', 0)
            self.coverage = defense.get_defense_score()
        except: pass
        self.hovered = self.rect.collidepoint(mpos)

    def handle_click(self, mpos):
        if self.rect.collidepoint(mpos):
            if self.on_click:
                try: self.on_click()
                except: pass
            return True
        return False

    def draw(self, screen):
        bg = Theme.PANEL_HOVER if self.hovered else Theme.PANEL_BG
        pygame.draw.rect(screen, bg, self.rect, border_radius=5)
        bc = Theme.NEON_GREEN if self.active == self.total and self.total > 0 else (Theme.NEON_YELLOW if self.active > 0 else Theme.NEON_RED)
        pygame.draw.rect(screen, bc, self.rect, 2, border_radius=5)
        screen.blit(self.font.render(f"FW: {self.active}/{self.total}", True, bc), (self.rect.x+8, self.rect.y+4))

        bx, by = self.rect.x+8, self.rect.y+24
        bw = self.rect.w - 16
        pygame.draw.rect(screen, (30,35,45), (bx, by, bw, 8), border_radius=4)
        cw = int(bw * self.coverage / 100)
        if cw > 0:
            cc = Theme.NEON_GREEN if self.coverage >= 60 else (Theme.NEON_YELLOW if self.coverage >= 30 else Theme.NEON_RED)
            pygame.draw.rect(screen, cc, (bx, by, cw, 8), border_radius=4)
        screen.blit(self.fs.render(f"Coverage: {self.coverage}%", True, Theme.TEXT_DIM), (bx, by+12))
        if self.hovered:
            screen.blit(self.fs.render("[F] rules", True, Theme.TEXT_DIM), (self.rect.x+5, self.rect.y+self.rect.h+2))
