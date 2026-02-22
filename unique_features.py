"""
===========================================================
FILE: unique_features.py
PURPOSE: Truly unique features never seen in games before
===========================================================

FEATURES:
1. AI Threat Predictor - Predicts attacks before they happen
2. Hacker Chat Interceptor - Fake intercepted messages
3. Network Heartbeat Monitor - ECG-style pulse
4. Cyber News Ticker - Scrolling news feed
5. Attack Fingerprint - Unique visual per attacker

===========================================================
"""

import pygame
import random
import math
import time
from typing import List, Dict

print("[UNIQUE] Loading unique features...")


# ============================================
# AI THREAT PREDICTOR
# ============================================

class AIThreatPredictor:
    """
    Simulates AI predicting the next attack.
    Shows prediction with confidence percentage.
    Very impressive - shows "machine learning" concept!
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
        self.attack_history = []
        self.prediction = None
        self.confidence = 0
        self.thinking = False
        self.think_progress = 0
        self.last_prediction_time = 0
        self.prediction_interval = 5  # Predict every 5 seconds
        
        self.attack_types = ['DDoS', 'SYN Flood', 'Port Scan', 'Brute Force', 'Malware']
        self.attack_colors = {
            'DDoS': (255, 50, 50),
            'SYN Flood': (255, 150, 0),
            'Port Scan': (255, 255, 0),
            'Brute Force': (200, 0, 255),
            'Malware': (0, 255, 150)
        }
        
        self.scan_line = 0
        
        print("[AI] ✅ Threat Predictor initialized")
    
    def add_attack(self, attack_type: str):
        """Record an attack for learning."""
        self.attack_history.append({
            'type': attack_type,
            'time': time.time()
        })
        
        # Keep only last 50 attacks
        if len(self.attack_history) > 50:
            self.attack_history.pop(0)
    
    def update(self):
        """Update prediction."""
        current_time = time.time()
        
        # Scan line animation
        self.scan_line = (self.scan_line + 2) % self.rect.height
        
        # Check if should make new prediction
        if current_time - self.last_prediction_time > self.prediction_interval:
            self.thinking = True
            self.think_progress = 0
        
        # Thinking animation
        if self.thinking:
            self.think_progress += 2
            
            if self.think_progress >= 100:
                self.thinking = False
                self._make_prediction()
                self.last_prediction_time = current_time
    
    def _make_prediction(self):
        """Make a prediction based on history."""
        if len(self.attack_history) < 3:
            # Not enough data - random prediction
            self.prediction = random.choice(self.attack_types)
            self.confidence = random.randint(45, 65)
        else:
            # Analyze history (simulated AI)
            type_counts = {}
            for attack in self.attack_history[-20:]:
                t = attack['type']
                type_counts[t] = type_counts.get(t, 0) + 1
            
            if type_counts:
                # Predict most common + some randomness
                most_common = max(type_counts, key=type_counts.get)
                
                if random.random() > 0.3:
                    self.prediction = most_common
                    self.confidence = min(95, 60 + type_counts[most_common] * 3)
                else:
                    self.prediction = random.choice(self.attack_types)
                    self.confidence = random.randint(40, 70)
            else:
                self.prediction = random.choice(self.attack_types)
                self.confidence = random.randint(50, 75)
    
    def draw(self, surface):
        """Draw the AI predictor panel."""
        # Background
        pygame.draw.rect(surface, (10, 20, 35), self.rect, border_radius=5)
        pygame.draw.rect(surface, (0, 255, 200), self.rect, 2, border_radius=5)
        
        # Title
        font_title = pygame.font.Font(None, 18)
        font_text = pygame.font.Font(None, 16)
        font_big = pygame.font.Font(None, 22)
        
        title = font_title.render("🤖 AI THREAT PREDICTOR", True, (0, 255, 200))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Scan line effect
        scan_y = self.rect.y + 25 + self.scan_line % (self.rect.height - 30)
        pygame.draw.line(surface, (0, 255, 200, 50), 
                        (self.rect.x + 5, scan_y), 
                        (self.rect.right - 5, scan_y), 1)
        
        if self.thinking:
            # Thinking animation
            progress_width = int((self.think_progress / 100) * (self.rect.width - 20))
            
            # "Analyzing" text
            analyze_text = font_text.render("ANALYZING PATTERNS...", True, (255, 255, 0))
            surface.blit(analyze_text, (self.rect.x + 10, self.rect.y + 35))
            
            # Progress bar
            pygame.draw.rect(surface, (30, 50, 70), 
                           (self.rect.x + 10, self.rect.y + 55, self.rect.width - 20, 15))
            pygame.draw.rect(surface, (0, 255, 200), 
                           (self.rect.x + 10, self.rect.y + 55, progress_width, 15))
            
            # Binary effect
            binary = ''.join([str(random.randint(0, 1)) for _ in range(20)])
            binary_text = font_text.render(binary, True, (0, 100, 80))
            surface.blit(binary_text, (self.rect.x + 10, self.rect.y + 75))
            
        elif self.prediction:
            # Show prediction
            pred_label = font_text.render("NEXT ATTACK PREDICTION:", True, (150, 150, 150))
            surface.blit(pred_label, (self.rect.x + 10, self.rect.y + 30))
            
            # Attack type
            color = self.attack_colors.get(self.prediction, (255, 255, 255))
            pred_text = font_big.render(self.prediction.upper(), True, color)
            surface.blit(pred_text, (self.rect.x + 10, self.rect.y + 48))
            
            # Confidence bar
            conf_label = font_text.render(f"Confidence: {self.confidence}%", True, (150, 150, 150))
            surface.blit(conf_label, (self.rect.x + 10, self.rect.y + 72))
            
            bar_width = int((self.confidence / 100) * (self.rect.width - 20))
            
            # Color based on confidence
            if self.confidence > 80:
                bar_color = (0, 255, 100)
            elif self.confidence > 60:
                bar_color = (255, 200, 0)
            else:
                bar_color = (255, 100, 50)
            
            pygame.draw.rect(surface, (30, 50, 70), 
                           (self.rect.x + 10, self.rect.y + 90, self.rect.width - 20, 10))
            pygame.draw.rect(surface, bar_color, 
                           (self.rect.x + 10, self.rect.y + 90, bar_width, 10))
        else:
            # Initializing
            init_text = font_text.render("Initializing AI...", True, (100, 100, 100))
            surface.blit(init_text, (self.rect.x + 10, self.rect.y + 50))


# ============================================
# HACKER CHAT INTERCEPTOR
# ============================================

class HackerChatInterceptor:
    """
    Shows fake intercepted hacker communications.
    Very dramatic and unique!
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
        self.messages = []
        self.max_messages = 5
        self.last_message_time = 0
        self.message_interval = 4  # New message every 4 seconds
        
        # Hacker names
        self.hackers = [
            "DarkShadow_X",
            "CyberPhantom",
            "NullByte_99",
            "R00tK1ll3r",
            "ZeroDay_Hax",
            "AnonymousZ",
            "BlackHat_Pro",
            "GhostShell",
            "Cr4ck3r_X",
            "MalwareKing"
        ]
        
        # Message templates
        self.message_templates = [
            "Target acquired. Initiating attack.",
            "Firewall detected. Switching vectors.",
            "Sending payload now...",
            "Port scan complete. Found {} open ports.",
            "DDoS bots online. Ready to flood.",
            "Password hash captured. Cracking...",
            "Injecting malicious code...",
            "Bypassing security... {}%",
            "We're in. Extracting data.",
            "Defense detected! Abort? No, continue.",
            "New vulnerability found. Exploiting.",
            "Botnet activated. {} nodes ready.",
            "Encryption breached. Reading files.",
            "Admin credentials obtained!",
            "Backdoor installed successfully.",
            "They're blocking us. Use backup route.",
            "Proxy chain established.",
            "VPN hopping... {} hops active.",
            "Target's IPS is weak. Push harder.",
            "SQL injection successful!"
        ]
        
        self.decrypt_effect = 0
        
        print("[CHAT] ✅ Hacker Chat Interceptor initialized")
    
    def update(self):
        """Update chat messages."""
        current_time = time.time()
        
        self.decrypt_effect = (self.decrypt_effect + 1) % 10
        
        # Add new message periodically
        if current_time - self.last_message_time > self.message_interval:
            self._add_message()
            self.last_message_time = current_time
    
    def _add_message(self):
        """Add a new intercepted message."""
        hacker = random.choice(self.hackers)
        template = random.choice(self.message_templates)
        
        # Fill in template placeholders
        if '{}' in template:
            if '%' in template:
                message = template.format(random.randint(50, 99))
            else:
                message = template.format(random.randint(3, 50))
        else:
            message = template
        
        self.messages.append({
            'hacker': hacker,
            'message': message,
            'time': time.time(),
            'decrypting': True,
            'decrypt_progress': 0
        })
        
        # Limit messages
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def trigger_message(self, context: str = None):
        """Trigger a contextual message."""
        if context == 'blocked':
            messages = [
                "They blocked us! Switch IP!",
                "Firewall caught that. Retry.",
                "Connection dropped. Reconnecting...",
                "Defense is strong. Need more bots."
            ]
        elif context == 'damage':
            messages = [
                "We got through! Keep pushing!",
                "Their network is weakening!",
                "Payload delivered successfully!",
                "Data exfiltration in progress..."
            ]
        elif context == 'boss':
            messages = [
                "Deploying main weapon now!",
                "All units focus fire!",
                "Maximum attack power!",
                "Target their main server!"
            ]
        else:
            return
        
        hacker = random.choice(self.hackers)
        message = random.choice(messages)
        
        self.messages.append({
            'hacker': hacker,
            'message': message,
            'time': time.time(),
            'decrypting': False,
            'decrypt_progress': 100
        })
        
        if len(self.messages) > self.max_messages:
            self.messages.pop(0)
    
    def draw(self, surface):
        """Draw the chat panel."""
        # Background
        pygame.draw.rect(surface, (15, 10, 20), self.rect, border_radius=5)
        pygame.draw.rect(surface, (255, 0, 100), self.rect, 2, border_radius=5)
        
        # Title with "intercepted" effect
        font_title = pygame.font.Font(None, 16)
        font_text = pygame.font.Font(None, 14)
        
        # Blinking indicator
        if self.decrypt_effect < 5:
            indicator = "●"
            ind_color = (255, 0, 0)
        else:
            indicator = "○"
            ind_color = (100, 0, 50)
        
        title = font_title.render(f"{indicator} INTERCEPTED COMMS", True, (255, 0, 100))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Encrypted label
        enc_label = font_text.render("[DECRYPTED]", True, (100, 100, 100))
        surface.blit(enc_label, (self.rect.right - 70, self.rect.y + 6))
        
        # Draw messages
        y_offset = 25
        for msg in self.messages[-4:]:
            # Update decryption
            if msg['decrypting']:
                msg['decrypt_progress'] += 5
                if msg['decrypt_progress'] >= 100:
                    msg['decrypting'] = False
            
            # Hacker name
            name_color = (255, 100, 150)
            name_text = font_text.render(f"[{msg['hacker']}]:", True, name_color)
            surface.blit(name_text, (self.rect.x + 5, self.rect.y + y_offset))
            
            # Message (with decrypt effect)
            if msg['decrypting']:
                # Show garbled text
                garble_amount = (100 - msg['decrypt_progress']) // 10
                display_text = ""
                for i, char in enumerate(msg['message'][:25]):
                    if random.random() < garble_amount / 10:
                        display_text += random.choice("@#$%&*!?")
                    else:
                        display_text += char
            else:
                display_text = msg['message'][:28]
                if len(msg['message']) > 28:
                    display_text += "..."
            
            msg_text = font_text.render(display_text, True, (200, 200, 200))
            surface.blit(msg_text, (self.rect.x + 8, self.rect.y + y_offset + 12))
            
            y_offset += 30


# ============================================
# NETWORK HEARTBEAT MONITOR
# ============================================

class NetworkHeartbeat:
    """
    ECG-style heartbeat monitor for network health.
    Like a hospital monitor - very visual!
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
        self.heartbeat_data = []
        self.max_points = 100
        self.pulse_phase = 0
        self.is_flatlining = False
        self.bpm = 60  # Beats per minute (network "pulse")
        self.last_health = 100
        
        self.beep_timer = 0
        self.show_beep = False
        
        print("[HEART] ✅ Network Heartbeat initialized")
    
    def update(self, health: float):
        """Update heartbeat based on health."""
        self.last_health = health
        self.pulse_phase += 0.15
        
        # Calculate BPM based on threat (inverse of health)
        if health > 70:
            self.bpm = 60
        elif health > 40:
            self.bpm = 90
        elif health > 20:
            self.bpm = 120
        else:
            self.bpm = 150
        
        # Check flatline
        self.is_flatlining = health <= 0
        
        # Generate heartbeat point
        if self.is_flatlining:
            point = 0.5  # Flatline
        else:
            # ECG-like pattern
            phase = self.pulse_phase % (2 * math.pi)
            
            if phase < 0.5:
                point = 0.5
            elif phase < 0.7:
                point = 0.5 + (phase - 0.5) * 2  # Rising
            elif phase < 0.9:
                point = 0.9 - (phase - 0.7) * 4  # Spike up then down
            elif phase < 1.1:
                point = 0.1 + (phase - 0.9) * 2  # Rising back
            else:
                point = 0.5
            
            # Add some noise based on health
            noise = (100 - health) / 500
            point += random.uniform(-noise, noise)
        
        self.heartbeat_data.append(point)
        
        if len(self.heartbeat_data) > self.max_points:
            self.heartbeat_data.pop(0)
        
        # Beep timer
        self.beep_timer += 1
        beep_interval = max(10, 60 - self.bpm // 3)
        if self.beep_timer >= beep_interval:
            self.show_beep = True
            self.beep_timer = 0
        else:
            self.show_beep = False
    
    def draw(self, surface):
        """Draw the heartbeat monitor."""
        # Background
        pygame.draw.rect(surface, (5, 15, 10), self.rect, border_radius=5)
        
        # Border color based on status
        if self.is_flatlining:
            border_color = (255, 0, 0)
        elif self.last_health < 30:
            border_color = (255, 100, 0)
        else:
            border_color = (0, 255, 100)
        
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=5)
        
        # Title
        font = pygame.font.Font(None, 16)
        title = font.render("💓 NETWORK PULSE", True, border_color)
        surface.blit(title, (self.rect.x + 5, self.rect.y + 3))
        
        # BPM display
        bpm_text = font.render(f"{self.bpm} BPM", True, border_color)
        surface.blit(bpm_text, (self.rect.right - 55, self.rect.y + 3))
        
        # Beep indicator
        if self.show_beep and not self.is_flatlining:
            pygame.draw.circle(surface, border_color, 
                             (self.rect.right - 70, self.rect.y + 10), 4)
        
        # Draw ECG line
        if len(self.heartbeat_data) > 1:
            graph_rect = pygame.Rect(
                self.rect.x + 5,
                self.rect.y + 18,
                self.rect.width - 10,
                self.rect.height - 23
            )
            
            # Grid lines
            for i in range(4):
                y = graph_rect.y + i * graph_rect.height // 3
                pygame.draw.line(surface, (20, 40, 30), 
                               (graph_rect.x, y), (graph_rect.right, y), 1)
            
            # Build points
            points = []
            for i, value in enumerate(self.heartbeat_data):
                x = graph_rect.x + (i * graph_rect.width // len(self.heartbeat_data))
                y = graph_rect.bottom - int(value * graph_rect.height)
                y = max(graph_rect.y, min(graph_rect.bottom, y))
                points.append((x, y))
            
            # Draw line
            if len(points) > 1:
                pygame.draw.lines(surface, border_color, False, points, 2)
                
                # Glow at current point
                if points:
                    pygame.draw.circle(surface, border_color, points[-1], 4)
        
        # Flatline warning
        if self.is_flatlining:
            warning_font = pygame.font.Font(None, 20)
            warning = warning_font.render("!! FLATLINE !!", True, (255, 0, 0))
            warning_rect = warning.get_rect(center=(self.rect.centerx, self.rect.centery))
            surface.blit(warning, warning_rect)


# ============================================
# CYBER NEWS TICKER
# ============================================

class CyberNewsTicker:
    """
    Scrolling news feed with cyber threat news.
    Professional look!
    """
    
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
            "🔍 Supply chain attack affects thousands of organizations",
            "📱 Mobile malware variants increased by 50%",
            "🏛️ Government agencies report coordinated cyber attacks",
            "💰 Cyber insurance claims reach all-time high",
            "🔐 Quantum-resistant encryption standards proposed",
            "🕵️ State-sponsored hackers target critical infrastructure"
        ]
        
        self.scroll_x = self.rect.width
        self.scroll_speed = 1.5
        self.current_news = random.choice(self.news_items)
        self.text_width = 0
        
        print("[NEWS] ✅ Cyber News Ticker initialized")
    
    def update(self):
        """Update scroll position."""
        self.scroll_x -= self.scroll_speed
        
        # Reset when scrolled off
        if self.scroll_x < -self.text_width - 50:
            self.scroll_x = self.rect.width
            self.current_news = random.choice(self.news_items)
    
    def add_breaking_news(self, news: str):
        """Add breaking news item."""
        self.current_news = f"🔴 BREAKING: {news}"
        self.scroll_x = self.rect.width
    
    def draw(self, surface):
        """Draw the news ticker."""
        # Background
        pygame.draw.rect(surface, (20, 10, 30), self.rect)
        pygame.draw.rect(surface, (100, 50, 150), self.rect, 1)
        
        # News icon
        font_icon = pygame.font.Font(None, 18)
        icon = font_icon.render("📰 NEWS", True, (150, 100, 200))
        surface.blit(icon, (self.rect.x + 5, self.rect.y + 4))
        
        # Scrolling text
        font = pygame.font.Font(None, 18)
        text = font.render(self.current_news, True, (220, 220, 255))
        self.text_width = text.get_width()
        
        # Create clip rect
        clip_rect = pygame.Rect(self.rect.x + 60, self.rect.y, self.rect.width - 65, self.rect.height)
        
        # Draw text with clipping
        text_x = self.rect.x + 60 + int(self.scroll_x)
        if text_x < self.rect.right and text_x + self.text_width > self.rect.x + 60:
            surface.set_clip(clip_rect)
            surface.blit(text, (text_x, self.rect.y + 4))
            surface.set_clip(None)


# ============================================
# ATTACK FINGERPRINT
# ============================================

class AttackFingerprint:
    """
    Generates unique visual fingerprint for each attacker.
    Like a forensics ID!
    """
    
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        
        self.current_fingerprint = None
        self.fingerprint_data = []
        self.attacker_ip = "---"
        self.attacker_country = "Unknown"
        self.threat_score = 0
        
        self.animation_phase = 0
        self.scan_complete = False
        
        print("[PRINT] ✅ Attack Fingerprint initialized")
    
    def analyze_attacker(self, ip: str, country: str = None, threat_level: int = None):
        """Generate fingerprint for an attacker."""
        self.attacker_ip = ip
        self.attacker_country = country or random.choice(['Russia', 'China', 'USA', 'Unknown', 'Germany', 'Brazil'])
        self.threat_score = threat_level or random.randint(30, 100)
        
        # Generate unique fingerprint based on IP
        random.seed(hash(ip))
        
        self.fingerprint_data = []
        for i in range(8):
            ring_data = {
                'radius': 10 + i * 8,
                'segments': random.randint(4, 12),
                'rotation': random.uniform(0, math.pi * 2),
                'color': (
                    random.randint(100, 255),
                    random.randint(50, 200),
                    random.randint(100, 255)
                )
            }
            self.fingerprint_data.append(ring_data)
        
        random.seed()  # Reset seed
        
        self.animation_phase = 0
        self.scan_complete = False
    
    def update(self):
        """Update fingerprint animation."""
        if not self.scan_complete:
            self.animation_phase += 2
            if self.animation_phase >= 100:
                self.scan_complete = True
        
        # Rotate rings
        for ring in self.fingerprint_data:
            ring['rotation'] += 0.02
    
    def draw(self, surface):
        """Draw the fingerprint panel."""
        # Background
        pygame.draw.rect(surface, (15, 15, 25), self.rect, border_radius=5)
        pygame.draw.rect(surface, (150, 50, 255), self.rect, 2, border_radius=5)
        
        # Title
        font_title = pygame.font.Font(None, 16)
        font_small = pygame.font.Font(None, 14)
        
        title = font_title.render("🔬 ATTACK FINGERPRINT", True, (150, 50, 255))
        surface.blit(title, (self.rect.x + 5, self.rect.y + 5))
        
        # Fingerprint visualization
        center_x = self.rect.x + self.rect.width // 4
        center_y = self.rect.centery + 10
        
        if self.fingerprint_data:
            # Draw rings
            max_ring = int((self.animation_phase / 100) * len(self.fingerprint_data))
            
            for i, ring in enumerate(self.fingerprint_data[:max_ring + 1]):
                alpha = 255 if i < max_ring else int((self.animation_phase % (100 / len(self.fingerprint_data))) * 2.55)
                
                # Draw segmented ring
                for seg in range(ring['segments']):
                    angle_start = ring['rotation'] + (seg * 2 * math.pi / ring['segments'])
                    angle_end = angle_start + (math.pi / ring['segments'])
                    
                    # Draw arc segment
                    start_pos = (
                        center_x + math.cos(angle_start) * ring['radius'],
                        center_y + math.sin(angle_start) * ring['radius']
                    )
                    end_pos = (
                        center_x + math.cos(angle_end) * ring['radius'],
                        center_y + math.sin(angle_end) * ring['radius']
                    )
                    
                    pygame.draw.line(surface, ring['color'], start_pos, end_pos, 2)
        
        # Info panel on right side
        info_x = self.rect.x + self.rect.width // 2
        
        ip_label = font_small.render("IP:", True, (100, 100, 100))
        surface.blit(ip_label, (info_x, self.rect.y + 25))
        
        ip_text = font_small.render(self.attacker_ip[:15], True, (200, 200, 200))
        surface.blit(ip_text, (info_x, self.rect.y + 38))
        
        country_label = font_small.render("Origin:", True, (100, 100, 100))
        surface.blit(country_label, (info_x, self.rect.y + 55))
        
        country_text = font_small.render(self.attacker_country, True, (200, 200, 200))
        surface.blit(country_text, (info_x, self.rect.y + 68))
        
        # Threat score
        threat_label = font_small.render("Threat:", True, (100, 100, 100))
        surface.blit(threat_label, (info_x, self.rect.y + 85))
        
        if self.threat_score > 70:
            threat_color = (255, 50, 50)
        elif self.threat_score > 40:
            threat_color = (255, 200, 0)
        else:
            threat_color = (50, 255, 50)
        
        threat_text = font_small.render(f"{self.threat_score}%", True, threat_color)
        surface.blit(threat_text, (info_x + 45, self.rect.y + 85))
        
        # Scan status
        if not self.scan_complete:
            scan_text = font_small.render(f"Scanning... {self.animation_phase}%", True, (255, 255, 0))
            surface.blit(scan_text, (self.rect.x + 10, self.rect.bottom - 18))
        else:
            scan_text = font_small.render("Analysis Complete", True, (0, 255, 100))
            surface.blit(scan_text, (self.rect.x + 10, self.rect.bottom - 18))


# ============================================
# TEST
# ============================================

if __name__ == "__main__":
    print("\nTesting Unique Features...")
    
    print("\n[TEST] AI Threat Predictor")
    ai = AIThreatPredictor(0, 0, 200, 110)
    ai.add_attack("DDoS")
    ai.add_attack("DDoS")
    ai._make_prediction()
    print(f"  Prediction: {ai.prediction} ({ai.confidence}%)")
    
    print("\n[TEST] Hacker Chat")
    chat = HackerChatInterceptor(0, 0, 200, 150)
    chat._add_message()
    print(f"  Messages: {len(chat.messages)}")
    
    print("\n[TEST] Network Heartbeat")
    heart = NetworkHeartbeat(0, 0, 200, 80)
    heart.update(75)
    print(f"  BPM: {heart.bpm}")
    
    print("\n[TEST] News Ticker")
    news = CyberNewsTicker(0, 0, 400, 25)
    print(f"  Current: {news.current_news[:40]}...")
    
    print("\n[TEST] Attack Fingerprint")
    fp = AttackFingerprint(0, 0, 200, 120)
    fp.analyze_attacker("192.168.1.100", "Russia", 85)
    print(f"  IP: {fp.attacker_ip}")
    print(f"  Country: {fp.attacker_country}")
    print(f"  Threat: {fp.threat_score}%")
    
    print("\n✅ All unique features working!")
