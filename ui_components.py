
"""
ui_components.py
UI Components for Cyber Defense Game

Author: Game UI Team
Description: Health bar, buttons, stats panel, and other UI elements
"""

import pygame
import math
import time


# ============================================
# COLOR THEME
# ============================================

class Theme:
    """Cyber defense color theme"""
    
    # Backgrounds
    DARK_BG = (10, 15, 25)
    PANEL_BG = (20, 30, 50)
    PANEL_BORDER = (40, 60, 90)
    
    # Neon accent colors
    NEON_BLUE = (0, 200, 255)
    NEON_GREEN = (0, 255, 150)
    NEON_RED = (255, 50, 80)
    NEON_YELLOW = (255, 220, 0)
    NEON_PURPLE = (180, 0, 255)
    NEON_ORANGE = (255, 150, 0)
    
    # Text colors
    TEXT_PRIMARY = (220, 230, 255)
    TEXT_SECONDARY = (150, 160, 180)
    TEXT_DANGER = (255, 100, 100)
    TEXT_SUCCESS = (100, 255, 150)
    
    # Health bar colors
    HEALTH_HIGH = (0, 255, 100)
    HEALTH_MEDIUM = (255, 220, 0)
    HEALTH_LOW = (255, 50, 80)


# ============================================
# HEALTH BAR
# ============================================

class HealthBar:
    """
    Animated health bar with gradient and pulse effects.
    
    Features:
    - Smooth value transitions
    - Color changes based on health level
    - Pulse effect when critical
    - Professional cyber look
    """
    
    def __init__(self, x, y, width, height, max_value=100, label="NETWORK HEALTH"):
        """
        Initialize health bar.
        
        Args:
            x: X position
            y: Y position
            width: Bar width
            height: Bar height
            max_value: Maximum health value
            label: Label text to display
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_value = max_value
        self.label = label
        
        # Current and display values (for smooth animation)
        self.current_value = max_value
        self.display_value = float(max_value)
        
        # Animation
        self.animation_speed = 0.08
        self.pulse_phase = 0
        self.pulse_speed = 0.15
        
        # Fonts (initialized lazily)
        self._font_label = None
        self._font_value = None
    
    def _init_fonts(self):
        """Initialize fonts if not already done"""
        try:
            if self._font_label is None:
                self._font_label = pygame.font.Font(None, 20)
            if self._font_value is None:
                self._font_value = pygame.font.Font(None, 24)
        except Exception as e:
            print(f"[ERROR] Font initialization failed: {e}")
    
    def set_value(self, value):
        """Set target health value (will animate to this)"""
        self.current_value = max(0, min(self.max_value, value))
    
    def update(self):
        """Update animation each frame"""
        # Smooth transition to target value
        diff = self.current_value - self.display_value
        self.display_value += diff * self.animation_speed
        
        # Clamp to prevent floating point issues
        if abs(diff) < 0.1:
            self.display_value = self.current_value
        
        # Update pulse animation
        self.pulse_phase += self.pulse_speed
    
    def get_health_color(self):
        """Get color based on current health percentage"""
        percentage = self.display_value / self.max_value
        
        if percentage > 0.7:
            return Theme.HEALTH_HIGH
        elif percentage > 0.3:
            return Theme.HEALTH_MEDIUM
        else:
            return Theme.HEALTH_LOW
    
    def draw(self, surface):
        """Draw the health bar"""
        try:
            self._init_fonts()
            
            # Calculate dimensions
            padding = 3
            inner_width = self.width - padding * 2
            inner_height = self.height - padding * 2
            fill_width = int((self.display_value / self.max_value) * inner_width)
            
            # ---- Draw background frame ----
            frame_rect = pygame.Rect(
                self.x - padding, 
                self.y - padding,
                self.width + padding * 2, 
                self.height + padding * 2
            )
            pygame.draw.rect(surface, Theme.PANEL_BG, frame_rect, border_radius=5)
            pygame.draw.rect(surface, Theme.PANEL_BORDER, frame_rect, 2, border_radius=5)
            
            # ---- Draw empty bar background ----
            empty_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(surface, (30, 15, 15), empty_rect, border_radius=3)
            
            # ---- Draw filled portion ----
            if fill_width > 0:
                fill_rect = pygame.Rect(
                    self.x + padding, 
                    self.y + padding,
                    fill_width, 
                    inner_height
                )
                
                # Get health color
                health_color = self.get_health_color()
                
                # Pulse effect when critical
                if self.current_value < 30:
                    pulse_intensity = abs(math.sin(self.pulse_phase)) * 40
                    health_color = (
                        min(255, health_color[0] + int(pulse_intensity)),
                        health_color[1],
                        health_color[2]
                    )
                
                # Draw main fill
                pygame.draw.rect(surface, health_color, fill_rect, border_radius=2)
                
                # Draw highlight/shine effect
                shine_rect = pygame.Rect(
                    self.x + padding,
                    self.y + padding,
                    fill_width,
                    inner_height // 3
                )
                shine_color = tuple(min(c + 50, 255) for c in health_color)
                pygame.draw.rect(surface, shine_color, shine_rect, border_radius=2)
            
            # ---- Draw label ----
            if self._font_label:
                label_surface = self._font_label.render(
                    self.label, True, Theme.TEXT_SECONDARY
                )
                surface.blit(label_surface, (self.x, self.y - 22))
            
            # ---- Draw percentage ----
            if self._font_value:
                percentage = int((self.display_value / self.max_value) * 100)
                value_text = f"{percentage}%"
                value_surface = self._font_value.render(
                    value_text, True, Theme.TEXT_PRIMARY
                )
                value_x = self.x + self.width - value_surface.get_width()
                surface.blit(value_surface, (value_x, self.y - 22))
                
        except Exception as e:
            print(f"[ERROR] Health bar draw failed: {e}")


# ============================================
# CYBER BUTTON
# ============================================

class CyberButton:
    """
    Stylized button with hover and click effects.
    
    Features:
    - Hover glow effect
    - Click animation
    - Customizable colors
    - Callback support
    """
    
    def __init__(self, x, y, width, height, text, 
                 color=None, callback=None, enabled=True):
        """
        Initialize button.
        
        Args:
            x: X position
            y: Y position
            width: Button width
            height: Button height
            text: Button text
            color: Button accent color (default: NEON_BLUE)
            callback: Function to call when clicked
            enabled: Whether button is clickable
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color if color else Theme.NEON_BLUE
        self.callback = callback
        self.enabled = enabled
        
        # State
        self.is_hovered = False
        self.is_pressed = False
        self.was_pressed = False
        
        # Animation
        self.glow_intensity = 0
        self.click_scale = 1.0
        
        # Font
        self._font = None
    
    def _init_font(self):
        """Initialize font lazily"""
        try:
            if self._font is None:
                self._font = pygame.font.Font(None, 22)
        except Exception as e:
            print(f"[ERROR] Button font failed: {e}")
    
    def set_enabled(self, enabled):
        """Enable or disable the button"""
        self.enabled = enabled
    
    def update(self, mouse_pos, mouse_pressed):
        """
        Update button state.
        
        Args:
            mouse_pos: Current mouse position (x, y)
            mouse_pressed: Mouse button states tuple
        """
        try:
            self.was_pressed = self.is_pressed
            self.is_hovered = self.rect.collidepoint(mouse_pos)
            self.is_pressed = self.is_hovered and mouse_pressed[0]
            
            # Trigger callback on release
            if self.was_pressed and not self.is_pressed and self.is_hovered:
                if self.callback and self.enabled:
                    try:
                        self.callback()
                    except Exception as e:
                        print(f"[ERROR] Button callback failed: {e}")
                    self.click_scale = 0.95
            
            # Animate glow
            if self.is_hovered and self.enabled:
                self.glow_intensity = min(1.0, self.glow_intensity + 0.15)
            else:
                self.glow_intensity = max(0.0, self.glow_intensity - 0.1)
            
            # Animate click scale
            self.click_scale = min(1.0, self.click_scale + 0.02)
            
        except Exception as e:
            print(f"[ERROR] Button update failed: {e}")
    
    def draw(self, surface):
        """Draw the button"""
        try:
            self._init_font()
            
            # Determine colors based on state
            if not self.enabled:
                bg_color = Theme.PANEL_BG
                border_color = Theme.PANEL_BORDER
                text_color = Theme.TEXT_SECONDARY
            elif self.is_pressed:
                bg_color = tuple(max(0, c - 30) for c in self.base_color)
                border_color = self.base_color
                text_color = Theme.TEXT_PRIMARY
            elif self.is_hovered:
                bg_color = Theme.PANEL_BG
                border_color = tuple(min(255, c + 30) for c in self.base_color)
                text_color = Theme.TEXT_PRIMARY
            else:
                bg_color = Theme.PANEL_BG
                border_color = self.base_color
                text_color = Theme.TEXT_PRIMARY
            
            # ---- Draw glow effect ----
            if self.glow_intensity > 0 and self.enabled:
                glow_rect = self.rect.inflate(15, 15)
                glow_surface = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
                glow_alpha = int(40 * self.glow_intensity)
                glow_color = (*self.base_color, glow_alpha)
                pygame.draw.rect(
                    glow_surface, glow_color,
                    glow_surface.get_rect(),
                    border_radius=10
                )
                surface.blit(glow_surface, glow_rect.topleft)
            
            # ---- Draw button body ----
            # Scale for click effect
            scaled_rect = self.rect.inflate(
                int((self.click_scale - 1) * 10),
                int((self.click_scale - 1) * 10)
            )
            
            pygame.draw.rect(surface, bg_color, scaled_rect, border_radius=5)
            pygame.draw.rect(surface, border_color, scaled_rect, 2, border_radius=5)
            
            # ---- Draw top highlight ----
            if self.enabled:
                highlight_rect = pygame.Rect(
                    scaled_rect.x + 3,
                    scaled_rect.y + 3,
                    scaled_rect.width - 6,
                    scaled_rect.height // 3
                )
                highlight_surface = pygame.Surface(highlight_rect.size, pygame.SRCALPHA)
                pygame.draw.rect(
                    highlight_surface,
                    (*border_color, 30),
                    highlight_surface.get_rect(),
                    border_radius=3
                )
                surface.blit(highlight_surface, highlight_rect.topleft)
            
            # ---- Draw text ----
            if self._font:
                text_surface = self._font.render(self.text, True, text_color)
                text_rect = text_surface.get_rect(center=scaled_rect.center)
                surface.blit(text_surface, text_rect)
                
        except Exception as e:
            print(f"[ERROR] Button draw failed: {e}")


# ============================================
# STATS PANEL
# ============================================

class StatsPanel:
    """
    Panel displaying game statistics.
    
    Features:
    - Multiple stat rows
    - Auto-updating values
    - Cyber-themed styling
    """
    
    def __init__(self, x, y, width, height, title="STATISTICS"):
        """
        Initialize stats panel.
        
        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            title: Panel title
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.stats = {}
        
        # Fonts
        self._font_title = None
        self._font_stat = None
    
    def _init_fonts(self):
        """Initialize fonts lazily"""
        try:
            if self._font_title is None:
                self._font_title = pygame.font.Font(None, 22)
            if self._font_stat is None:
                self._font_stat = pygame.font.Font(None, 20)
        except Exception as e:
            print(f"[ERROR] StatsPanel font failed: {e}")
    
    def set_stat(self, key, value):
        """Update a statistic value"""
        self.stats[key] = value
    
    def set_stats(self, stats_dict):
        """Update multiple statistics at once"""
        self.stats.update(stats_dict)
    
    def clear_stats(self):
        """Clear all statistics"""
        self.stats.clear()
    
    def draw(self, surface):
        """Draw the stats panel"""
        try:
            self._init_fonts()
            
            # ---- Draw panel background ----
            pygame.draw.rect(surface, Theme.PANEL_BG, self.rect, border_radius=8)
            pygame.draw.rect(surface, Theme.NEON_BLUE, self.rect, 2, border_radius=8)
            
            # ---- Draw title bar ----
            title_rect = pygame.Rect(
                self.rect.x, self.rect.y,
                self.rect.width, 30
            )
            pygame.draw.rect(
                surface, Theme.PANEL_BORDER, title_rect,
                border_top_left_radius=8,
                border_top_right_radius=8
            )
            
            # Title text
            if self._font_title:
                title_surface = self._font_title.render(
                    self.title, True, Theme.NEON_BLUE
                )
                surface.blit(
                    title_surface,
                    (self.rect.x + 12, self.rect.y + 7)
                )
            
            # ---- Draw stats ----
            if self._font_stat:
                y_offset = 42
                for key, value in self.stats.items():
                    # Key (left aligned)
                    key_surface = self._font_stat.render(
                        f"{key}:", True, Theme.TEXT_SECONDARY
                    )
                    surface.blit(
                        key_surface,
                        (self.rect.x + 12, self.rect.y + y_offset)
                    )
                    
                    # Value (right aligned)
                    value_text = str(value)
                    value_surface = self._font_stat.render(
                        value_text, True, Theme.TEXT_PRIMARY
                    )
                    value_x = self.rect.x + self.rect.width - value_surface.get_width() - 12
                    surface.blit(
                        value_surface,
                        (value_x, self.rect.y + y_offset)
                    )
                    
                    y_offset += 26
                    
        except Exception as e:
            print(f"[ERROR] StatsPanel draw failed: {e}")


# ============================================
# LOG PANEL
# ============================================

class LogPanel:
    """
    Panel showing recent event logs.
    
    Features:
    - Scrolling log entries
    - Color-coded by severity
    - Timestamp display
    """
    
    def __init__(self, x, y, width, height, title="EVENT LOG"):
        """
        Initialize log panel.
        
        Args:
            x: X position
            y: Y position
            width: Panel width
            height: Panel height
            title: Panel title
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.title = title
        self.logs = []
        self.max_logs = 50
        self.visible_logs = 8
        
        # Fonts
        self._font_title = None
        self._font_log = None
    
    def _init_fonts(self):
        """Initialize fonts lazily"""
        try:
            if self._font_title is None:
                self._font_title = pygame.font.Font(None, 20)
            if self._font_log is None:
                self._font_log = pygame.font.Font(None, 16)
        except Exception as e:
            print(f"[ERROR] LogPanel font failed: {e}")
    
    def add_log(self, message, log_type="info"):
        """
        Add a log entry.
        
        Args:
            message: Log message
            log_type: Type (info, warning, danger, success)
        """
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append({
            "time": timestamp,
            "message": message,
            "type": log_type
        })
        
        # Limit log size
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
    
    def clear_logs(self):
        """Clear all logs"""
        self.logs.clear()
    
    def _get_log_color(self, log_type):
        """Get color based on log type"""
        colors = {
            "info": Theme.NEON_BLUE,
            "warning": Theme.NEON_YELLOW,
            "danger": Theme.NEON_RED,
            "success": Theme.NEON_GREEN
        }
        return colors.get(log_type, Theme.TEXT_SECONDARY)
    
    def draw(self, surface):
        """Draw the log panel"""
        try:
            self._init_fonts()
            
            # ---- Draw panel background ----
            pygame.draw.rect(surface, Theme.PANEL_BG, self.rect, border_radius=8)
            pygame.draw.rect(surface, Theme.NEON_GREEN, self.rect, 2, border_radius=8)
            
            # ---- Draw title bar ----
            title_rect = pygame.Rect(
                self.rect.x, self.rect.y,
                self.rect.width, 28
            )
            pygame.draw.rect(
                surface, Theme.PANEL_BORDER, title_rect,
                border_top_left_radius=8,
                border_top_right_radius=8
            )
            
            # Title text
            if self._font_title:
                title_surface = self._font_title.render(
                    self.title, True, Theme.NEON_GREEN
                )
                surface.blit(
                    title_surface,
                    (self.rect.x + 10, self.rect.y + 6)
                )
            
            # ---- Draw log entries ----
            if self._font_log:
                y_offset = 35
                visible_logs = self.logs[-self.visible_logs:]
                
                for log in reversed(visible_logs):
                    log_color = self._get_log_color(log["type"])
                    
                    # Timestamp
                    time_surface = self._font_log.render(
                        log["time"], True, Theme.TEXT_SECONDARY
                    )
                    surface.blit(
                        time_surface,
                        (self.rect.x + 8, self.rect.y + y_offset)
                    )
                    
                    # Message (truncate if too long)
                    max_chars = 25
                    message = log["message"]
                    if len(message) > max_chars:
                        message = message[:max_chars-3] + "..."
                    
                    msg_surface = self._font_log.render(
                        message, True, log_color
                    )
                    surface.blit(
                        msg_surface,
                        (self.rect.x + 65, self.rect.y + y_offset)
                    )
                    
                    y_offset += 18
                    
        except Exception as e:
            print(f"[ERROR] LogPanel draw failed: {e}")


# ============================================
# THREAT LEVEL INDICATOR
# ============================================

class ThreatIndicator:
    """
    Visual indicator for current threat level.
    
    Features:
    - Color-coded threat levels
    - Animated pulsing when high
    - Smooth transitions
    """
    
    def __init__(self, x, y, width=120, height=50):
        """
        Initialize threat indicator.
        
        Args:
            x: X position
            y: Y position
            width: Indicator width
            height: Indicator height
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.threat_level = 0  # 0-100
        self.display_level = 0.0
        self.pulse_phase = 0
        
        # Fonts
        self._font = None
    
    def _init_font(self):
        """Initialize font lazily"""
        try:
            if self._font is None:
                self._font = pygame.font.Font(None, 18)
        except Exception:
            pass
    
    def set_level(self, level):
        """Set threat level (0-100)"""
        self.threat_level = max(0, min(100, level))
    
    def update(self):
        """Update animation"""
        # Smooth transition
        diff = self.threat_level - self.display_level
        self.display_level += diff * 0.1
        
        # Pulse when high threat
        if self.threat_level > 60:
            self.pulse_phase += 0.15
    
    def _get_threat_color(self):
        """Get color based on threat level"""
        if self.display_level > 70:
            return Theme.NEON_RED
        elif self.display_level > 40:
            return Theme.NEON_ORANGE
        elif self.display_level > 20:
            return Theme.NEON_YELLOW
        else:
            return Theme.NEON_GREEN
    
    def _get_threat_text(self):
        """Get threat level text"""
        if self.threat_level > 70:
            return "CRITICAL"
        elif self.threat_level > 40:
            return "HIGH"
        elif self.threat_level > 20:
            return "MODERATE"
        else:
            return "LOW"
    
    def draw(self, surface):
        """Draw the threat indicator"""
        try:
            self._init_font()
            
            # Background
            pygame.draw.rect(surface, Theme.PANEL_BG, self.rect, border_radius=5)
            
            # Border color based on threat
            border_color = self._get_threat_color()
            
            # Pulse effect for high threat
            if self.threat_level > 60:
                pulse = abs(math.sin(self.pulse_phase)) * 50
                border_color = (
                    min(255, border_color[0] + int(pulse)),
                    border_color[1],
                    border_color[2]
                )
            
            pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
            
            # Label
            if self._font:
                label = self._font.render("THREAT LEVEL", True, Theme.TEXT_SECONDARY)
                surface.blit(label, (self.rect.x + 10, self.rect.y + 5))
                
                # Level text
                level_text = self._get_threat_text()
                level_surface = self._font.render(level_text, True, border_color)
                surface.blit(level_surface, (self.rect.x + 10, self.rect.y + 25))
                
                # Percentage
                percent_text = f"{int(self.display_level)}%"
                percent_surface = self._font.render(percent_text, True, Theme.TEXT_PRIMARY)
                percent_x = self.rect.right - percent_surface.get_width() - 10
                surface.blit(percent_surface, (percent_x, self.rect.y + 25))
                
        except Exception as e:
            print(f"[ERROR] ThreatIndicator draw failed: {e}")


# ============================================
# DEFENSE MODE TOGGLE
# ============================================

class DefenseModeToggle:
    """
    Toggle switch for defense mode (Manual/Auto).
    
    Features:
    - Visual on/off states
    - Animated transition
    - Status LED indicator
    """
    
    def __init__(self, x, y, width=150, height=40, callback=None):
        """
        Initialize defense mode toggle.
        
        Args:
            x: X position
            y: Y position
            width: Toggle width
            height: Toggle height
            callback: Function to call on toggle
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.is_auto = False
        self.callback = callback
        
        # Animation
        self.toggle_position = 0.0  # 0 = Manual, 1 = Auto
        self.led_blink = 0
        
        # Font
        self._font = None
    
    def _init_font(self):
        """Initialize font lazily"""
        try:
            if self._font is None:
                self._font = pygame.font.Font(None, 18)
        except Exception:
            pass
    
    def toggle(self):
        """Toggle between modes"""
        self.is_auto = not self.is_auto
        if self.callback:
            try:
                self.callback(self.is_auto)
            except Exception as e:
                print(f"[ERROR] Toggle callback failed: {e}")
    
    def set_mode(self, is_auto):
        """Set mode directly"""
        self.is_auto = is_auto
    
    def update(self, mouse_pos, mouse_click):
        """Update toggle state"""
        # Animate toggle position
        target = 1.0 if self.is_auto else 0.0
        self.toggle_position += (target - self.toggle_position) * 0.2
        
        # Blink LED when auto
        if self.is_auto:
            self.led_blink += 0.1
        
        # Check for click
        if mouse_click and self.rect.collidepoint(mouse_pos):
            self.toggle()
    
    def draw(self, surface):
        """Draw the toggle"""
        try:
            self._init_font()
            
            # Background
            pygame.draw.rect(surface, Theme.PANEL_BG, self.rect, border_radius=5)
            
            # Border
            border_color = Theme.NEON_GREEN if self.is_auto else Theme.NEON_YELLOW
            pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
            
            # LED indicator
            led_x = self.rect.x + 15
            led_y = self.rect.centery
            
            if self.is_auto:
                # Blinking green LED
                blink = abs(math.sin(self.led_blink)) > 0.5
                led_color = Theme.NEON_GREEN if blink else (0, 100, 50)
            else:
                led_color = Theme.NEON_YELLOW
            
            pygame.draw.circle(surface, led_color, (led_x, led_y), 6)
            pygame.draw.circle(surface, Theme.TEXT_PRIMARY, (led_x, led_y), 6, 1)
            
            # Mode text
            if self._font:
                mode_text = "AUTO DEFENSE" if self.is_auto else "MANUAL MODE"
                status_text = "ACTIVE" if self.is_auto else "STANDBY"
                
                text_surface = self._font.render(mode_text, True, Theme.TEXT_PRIMARY)
                surface.blit(text_surface, (self.rect.x + 30, self.rect.y + 8))
                
                status_surface = self._font.render(status_text, True, border_color)
                surface.blit(status_surface, (self.rect.x + 30, self.rect.y + 23))
                
        except Exception as e:
            print(f"[ERROR] DefenseModeToggle draw failed: {e}")


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("ui_components.py - UI Components Module")
    print("This module should be imported, not run directly.")
    print("Classes available: HealthBar, CyberButton, StatsPanel, LogPanel, ThreatIndicator, DefenseModeToggle")
