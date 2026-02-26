"""
===========================================================
FILE: unique_features.py
PURPOSE: Network Heartbeat, Cyber News Ticker
===========================================================
"""

import pygame
import random
import math
import time

print("[UNIQUE] Loading unique features...")


# ============================================
# NETWORK HEARTBEAT MONITOR
# ============================================

class NetworkHeartbeat:
    """ECG-style heartbeat monitor for network health."""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
        self.heartbeat_data = []
        self.max_points = 100
        self.pulse_phase = 0
        self.is_flatlining = False
        self.bpm = 60
        self.last_health = 100
        
        self.beep_timer = 0
        self.show_beep = False
        
        print("[HEART] ✅ Network Heartbeat initialized")
    
    def update(self, health: float):
        """Update heartbeat based on health."""
        self.last_health = health
        self.pulse_phase += 0.15
        
        if health > 70:
            self.bpm = 60
        elif health > 40:
            self.bpm = 90
        elif health > 20:
            self.bpm = 120
        else:
            self.bpm = 150
        
        self.is_flatlining = health <= 0
        
        if self.is_flatlining:
            point = 0.5
        else:
            phase = self.pulse_phase % (2 * math.pi)
            
            if phase < 0.5:
                point = 0.5
            elif phase < 0.7:
                point = 0.5 + (phase - 0.5) * 2
            elif phase < 0.9:
                point = 0.9 - (phase - 0.7) * 4
            elif phase < 1.1:
                point = 0.1 + (phase - 0.9) * 2
            else:
                point = 0.5
            
            noise = (100 - health) / 500
            point += random.uniform(-noise, noise)
        
        self.heartbeat_data.append(point)
        
        if len(self.heartbeat_data) > self.max_points:
            self.heartbeat_data.pop(0)
        
        self.beep_timer += 1
        beep_interval = max(10, 60 - self.bpm // 3)
        if self.beep_timer >= beep_interval:
            self.show_beep = True
            self.beep_timer = 0
        else:
            self.show_beep = False
    
    def draw(self, surface):
        """Draw the heartbeat monitor."""
        pygame.draw.rect(surface, (5, 15, 10), self.rect, border_radius=5)
        
        if self.is_flatlining:
            border_color = (255, 0, 0)
        elif self.last_health < 30:
            border_color = (255, 100, 0)
        else:
            border_color = (0, 255, 100)
        
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
        
        font = pygame.font.Font(None, 16)
        title = font.render("NETWORK PULSE", True, border_color)
        surface.blit(title, (self.rect.x + 5, self.rect.y + 3))
        
        bpm_text = font.render(f"{self.bpm} BPM", True, border_color)
        surface.blit(bpm_text, (self.rect.right - 55, self.rect.y + 3))
        
        if self.show_beep and not self.is_flatlining:
            pygame.draw.circle(surface, border_color, (self.rect.right - 70, self.rect.y + 10), 4)
        
        if len(self.heartbeat_data) > 1:
            graph_rect = pygame.Rect(
                self.rect.x + 5,
                self.rect.y + 18,
                self.rect.width - 10,
                self.rect.height - 23
            )
            
            for i in range(4):
                y = graph_rect.y + i * graph_rect.height // 3
                pygame.draw.line(surface, (20, 40, 30), (graph_rect.x, y), (graph_rect.right, y), 1)
            
            points = []
            for i, value in enumerate(self.heartbeat_data):
                x = graph_rect.x + (i * graph_rect.width // len(self.heartbeat_data))
                y = graph_rect.bottom - int(value * graph_rect.height)
                y = max(graph_rect.y, min(graph_rect.bottom, y))
                points.append((x, y))
            
            if len(points) > 1:
                pygame.draw.lines(surface, border_color, False, points, 2)
                
                if points:
                    pygame.draw.circle(surface, border_color, points[-1], 4)
        
        if self.is_flatlining:
            warning_font = pygame.font.Font(None, 20)
            warning = warning_font.render("!! FLATLINE !!", True, (255, 0, 0))
            warning_rect = warning.get_rect(center=(self.rect.centerx, self.rect.centery))
            surface.blit(warning, warning_rect)


# ============================================
# CYBER NEWS TICKER
# ============================================

class CyberNewsTicker:
    """Scrolling news feed with cyber threat news."""
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
        self.news_items = [
            "🔴 BREAKING: New zero-day vulnerability discovered in enterprise systems",
            "⚠️ ALERT: Ransomware attacks up 300% this quarter",
            "🌐 Global botnet detected with over 500,000 compromised devices",
            "🔒 Security patch released for critical infrastructure systems",
            "💀 Dark web marketplace selling stolen credentials",
            "🚨 APT group targeting financial institutions worldwide",
            "📊 Cryptojacking attacks surge amid crypto price increase",
            "🛡️ New AI-powered defense system shows promising results",
            "⚡ DDoS attack peaks at 3.2 Tbps - new record",
            "🔍 Supply chain attack affects thousands of organizations"
        ]
        
        self.scroll_x = self.rect.width
        self.scroll_speed = 1.5
        self.current_news = random.choice(self.news_items)
        self.text_width = 0
        
        print("[NEWS] ✅ Cyber News Ticker initialized")
    
    def update(self):
        """Update scroll position."""
        self.scroll_x -= self.scroll_speed
        
        if self.scroll_x < -self.text_width - 50:
            self.scroll_x = self.rect.width
            self.current_news = random.choice(self.news_items)
    
    def add_breaking_news(self, news: str):
        """Add breaking news item."""
        self.current_news = f"🔴 BREAKING: {news}"
        self.scroll_x = self.rect.width
    
    def draw(self, surface):
        """Draw the news ticker."""
        pygame.draw.rect(surface, (20, 10, 30), self.rect)
        pygame.draw.rect(surface, (100, 50, 150), self.rect, 1)
        
        font_icon = pygame.font.Font(None, 18)
        icon = font_icon.render("NEWS", True, (150, 100, 200))
        surface.blit(icon, (self.rect.x + 5, self.rect.y + 4))
        
        font = pygame.font.Font(None, 18)
        text = font.render(self.current_news, True, (220, 220, 255))
        self.text_width = text.get_width()
        
        clip_rect = pygame.Rect(self.rect.x + 50, self.rect.y, self.rect.width - 55, self.rect.height)
        
        text_x = self.rect.x + 50 + int(self.scroll_x)
        if text_x < self.rect.right and text_x + self.text_width > self.rect.x + 50:
            surface.set_clip(clip_rect)
            surface.blit(text, (text_x, self.rect.y + 4))
            surface.set_clip(None)


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\nTesting Unique Features...")
    
    print("\n[TEST] Network Heartbeat")
    heart = NetworkHeartbeat(0, 0, 200, 80)
    heart.update(75)
    print(f"  BPM: {heart.bpm}")
    
    print("\n[TEST] News Ticker")
    news = CyberNewsTicker(0, 0, 400, 25)
    print(f"  News: {news.current_news[:30]}...")
    
    print("\n✅ All features working!")
