
"""
main.py
Main Game Loop for Cyber Defense Simulation

Author: Game UI Team
Description: Connects all modules, runs game loop, handles input
"""

import pygame
import sys
import random
import math
from queue import Queue, Empty
from enum import Enum

# Import our modules
try:
    from sprites import PacketSprite, NetworkNode, ParticleSystem, PacketType
    from ui_components import (
        HealthBar, CyberButton, StatsPanel, LogPanel,
        ThreatIndicator, DefenseModeToggle, Theme
    )
except ImportError as e:
    print(f"[ERROR] Failed to import modules: {e}")
    print("Make sure sprites.py and ui_components.py are in the same directory.")
    sys.exit(1)


# ============================================
# GAME CONFIGURATION
# ============================================

class Config:
    """Game configuration constants"""
    
    # Window settings
    SCREEN_WIDTH = 1200
    SCREEN_HEIGHT = 700
    FPS = 60
    TITLE = "PACKET DEFENDER - Cyber Defense Simulation"
    
    # Game area layout
    GAME_AREA_X = 250
    GAME_AREA_Y = 60
    GAME_AREA_WIDTH = 700
    GAME_AREA_HEIGHT = 580
    
    # Side panel
    SIDE_PANEL_X = 960
    SIDE_PANEL_WIDTH = 230
    
    # Control panel
    CONTROL_PANEL_X = 10
    CONTROL_PANEL_WIDTH = 230
    
    # Game settings
    MAX_HEALTH = 100
    MAX_PACKETS = 80
    PACKET_SPAWN_RATE = 0.03  # Probability per frame
    
    # Colors
    BG_COLOR = (10, 15, 25)
    GRID_COLOR = (25, 35, 55)


# ============================================
# GAME STATE
# ============================================

class GameState(Enum):
    """Possible game states"""
    RUNNING = "running"
    PAUSED = "paused"
    GAME_OVER = "game_over"


# ============================================
# MAIN GAME CLASS
# ============================================

class CyberDefenseGame:
    """
    Main game class that manages everything.
    
    Features:
    - Connects with packet capture module via queue
    - Connects with logging module via callback
    - Connects with defense module for blocking
    - Full game loop with proper error handling
    """
    
    def __init__(self, packet_queue=None, log_callback=None, block_callback=None):
        """
        Initialize the game.
        
        Args:
            packet_queue: Queue to receive packets from sniffer (optional)
            log_callback: Function to send logs to logger (optional)
            block_callback: Function to call defense module (optional)
        """
        # ---- Initialize Pygame ----
        try:
            pygame.init()
            pygame.display.set_caption(Config.TITLE)
            self.screen = pygame.display.set_mode(
                (Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT)
            )
            self.clock = pygame.time.Clock()
            print("[OK] Pygame initialized successfully")
        except pygame.error as e:
            print(f"[FATAL] Pygame initialization failed: {e}")
            sys.exit(1)
        
        # ---- External Connections ----
        self.packet_queue = packet_queue if packet_queue else Queue()
        self.log_callback = log_callback if log_callback else self._default_log
        self.block_callback = block_callback if block_callback else self._default_block
        
        # ---- Game State ----
        self.state = GameState.RUNNING
        self.running = True
        self.game_time = 0
        
        # ---- Game Data ----
        self.network_health = Config.MAX_HEALTH
        self.packets_processed = 0
        self.packets_blocked = 0
        self.threat_level = 0
        self.defense_mode = "MANUAL"
        self.blocked_ips = set()
        
        # ---- Sprite Groups ----
        self.packet_sprites = pygame.sprite.Group()
        self.node_sprites = pygame.sprite.Group()
        
        # ---- Effects ----
        self.particle_system = ParticleSystem()
        
        # ---- Initialize Components ----
        self._init_nodes()
        self._init_ui()
        
        print("[OK] Game initialized successfully")
        self.log_callback("System initialized", "success")
    
    def _default_log(self, message, log_type="info"):
        """Default logging when no external logger"""
        print(f"[LOG/{log_type.upper()}] {message}")
        # Also add to internal log panel
        if hasattr(self, 'log_panel'):
            self.log_panel.add_log(message, log_type)
    
    def _default_block(self, ip):
        """Default block action when no external defense module"""
        print(f"[BLOCK] IP blocked: {ip}")
        self.blocked_ips.add(ip)
    
    # ============================================
    # INITIALIZATION
    # ============================================
    
    def _init_nodes(self):
        """Initialize network topology"""
        try:
            center_x = Config.GAME_AREA_X + Config.GAME_AREA_WIDTH // 2
            center_y = Config.GAME_AREA_Y + Config.GAME_AREA_HEIGHT // 2
            
            # Main server (target)
            self.main_server = NetworkNode(
                center_x + 50, center_y,
                NetworkNode.SERVER, "MAIN-SERVER"
            )
            self.node_sprites.add(self.main_server)
            
            # Firewall
            self.firewall = NetworkNode(
                center_x - 100, center_y,
                NetworkNode.FIREWALL, "FIREWALL"
            )
            self.node_sprites.add(self.firewall)
            
            # Router (packet spawn point)
            self.router = NetworkNode(
                Config.GAME_AREA_X + 80, center_y,
                NetworkNode.ROUTER, "ROUTER"
            )
            self.node_sprites.add(self.router)
            
            # Workstations
            workstation_positions = [
                (center_x + 180, center_y - 120),
                (center_x + 180, center_y + 120),
                (center_x + 100, center_y - 200),
                (center_x + 100, center_y + 200),
            ]
            
            self.workstations = []
            for i, pos in enumerate(workstation_positions):
                ws = NetworkNode(pos[0], pos[1], NetworkNode.WORKSTATION, f"WS-0{i+1}")
                self.node_sprites.add(ws)
                self.workstations.append(ws)
            
            print(f"[OK] Network topology initialized with {len(self.node_sprites)} nodes")
            
        except Exception as e:
            print(f"[ERROR] Node initialization failed: {e}")
    
    def _init_ui(self):
        """Initialize all UI components"""
        try:
            # ---- Health Bar ----
            self.health_bar = HealthBar(
                Config.GAME_AREA_X + 20,
                Config.GAME_AREA_Y + 20,
                200, 22,
                Config.MAX_HEALTH,
                "NETWORK HEALTH"
            )
            
            # ---- Threat Indicator ----
            self.threat_indicator = ThreatIndicator(
                Config.GAME_AREA_X + 250,
                Config.GAME_AREA_Y + 10,
                140, 45
            )
            
            # ---- Defense Mode Toggle ----
            self.defense_toggle = DefenseModeToggle(
                Config.CONTROL_PANEL_X + 10,
                70,
                Config.CONTROL_PANEL_WIDTH - 20,
                45,
                self._on_defense_mode_change
            )
            
            # ---- Control Buttons ----
            self.buttons = []
            button_configs = [
                ("BLOCK THREATS", Theme.NEON_RED, self._action_block_threats),
                ("HEAL NETWORK", Theme.NEON_BLUE, self._action_heal_network),
                ("CLEAR ALL", Theme.NEON_ORANGE, self._action_clear_all),
                ("PAUSE GAME", Theme.NEON_YELLOW, self._action_toggle_pause),
            ]
            
            for i, (text, color, callback) in enumerate(button_configs):
                btn = CyberButton(
                    Config.CONTROL_PANEL_X + 10,
                    130 + i * 50,
                    Config.CONTROL_PANEL_WIDTH - 20,
                    40,
                    text, color, callback
                )
                self.buttons.append(btn)
            
            # ---- Stats Panel ----
            self.stats_panel = StatsPanel(
                Config.SIDE_PANEL_X,
                Config.GAME_AREA_Y,
                Config.SIDE_PANEL_WIDTH,
                180,
                "NETWORK STATS"
            )
            
            # ---- Log Panel ----
            self.log_panel = LogPanel(
                Config.SIDE_PANEL_X,
                Config.GAME_AREA_Y + 200,
                Config.SIDE_PANEL_WIDTH,
                180,
                "EVENT LOG"
            )
            
            print("[OK] UI components initialized")
            
        except Exception as e:
            print(f"[ERROR] UI initialization failed: {e}")
    
    # ============================================
    # CALLBACKS & ACTIONS
    # ============================================
    
    def _on_defense_mode_change(self, is_auto):
        """Called when defense mode is toggled"""
        self.defense_mode = "AUTO" if is_auto else "MANUAL"
        status = "activated" if is_auto else "deactivated"
        self.log_callback(f"Auto-defense {status}", "success" if is_auto else "warning")
    
    def _action_block_threats(self):
        """Block all visible threats"""
        blocked = 0
        for packet in self.packet_sprites:
            if packet.packet_type in [PacketType.SUSPICIOUS, PacketType.MALICIOUS]:
                if not packet.is_blocked:
                    packet.block()
                    self.packets_blocked += 1
                    blocked += 1
                    self.particle_system.emit_block_effect(packet.x, packet.y)
                    self.block_callback(packet.source_ip)
        
        if blocked > 0:
            self.log_callback(f"Blocked {blocked} threats", "danger")
    
    def _action_heal_network(self):
        """Heal the network"""
        heal_amount = 25
        old_health = self.network_health
        self.network_health = min(Config.MAX_HEALTH, self.network_health + heal_amount)
        
        if self.network_health > old_health:
            self.log_callback(f"Network healed +{heal_amount} HP", "success")
    
    def _action_clear_all(self):
        """Clear all packets from screen"""
        count = len(self.packet_sprites)
        for packet in list(self.packet_sprites):
            self.particle_system.emit_block_effect(packet.x, packet.y)
            packet.kill()
        
        self.threat_level = 0
        self.log_callback(f"Cleared {count} packets", "info")
    
    def _action_toggle_pause(self):
        """Toggle pause state"""
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
            self.log_callback("Game PAUSED", "warning")
        else:
            self.state = GameState.RUNNING
            self.log_callback("Game RESUMED", "info")
    
    # ============================================
    # PACKET MANAGEMENT
    # ============================================
    
    def _process_external_packets(self):
        """Process packets from external queue (packet sniffer)"""
        try:
            while True:
                data = self.packet_queue.get_nowait()
                
                if isinstance(data, dict):
                    self._spawn_packet(
                        source_ip=data.get('src', '0.0.0.0'),
                        dest_ip=data.get('dst', '0.0.0.0'),
                        protocol=data.get('proto', 'TCP'),
                        packet_type=data.get('type')
                    )
                elif isinstance(data, str):
                    self._spawn_packet(source_ip=data)
                    
        except Empty:
            pass
        except Exception as e:
            print(f"[ERROR] Processing external packet failed: {e}")
    
    def _spawn_packet(self, source_ip="0.0.0.0", dest_ip="0.0.0.0", 
                      protocol="TCP", packet_type=None):
        """Spawn a new packet sprite"""
        try:
            # Check limit
            if len(self.packet_sprites) >= Config.MAX_PACKETS:
                return
            
            # Check if IP is blocked
            if source_ip in self.blocked_ips:
                return
            
            # Determine packet type if not specified
            if packet_type is None:
                packet_type = self._classify_packet(source_ip)
            elif isinstance(packet_type, str):
                type_map = {
                    'safe': PacketType.SAFE,
                    'suspicious': PacketType.SUSPICIOUS,
                    'malicious': PacketType.MALICIOUS,
                    'blocked': PacketType.BLOCKED
                }
                packet_type = type_map.get(packet_type.lower(), PacketType.SAFE)
            
            # Create packet from router to server
            packet = PacketSprite(
                self.router.x, self.router.y,
                self.main_server.x, self.main_server.y,
                packet_type,
                source_ip, dest_ip, protocol
            )
            
            self.packet_sprites.add(packet)
            self.packets_processed += 1
            
            # Auto-defense
            if self.defense_mode == "AUTO" and packet_type == PacketType.MALICIOUS:
                packet.block()
                self.packets_blocked += 1
                self.block_callback(source_ip)
                self.log_callback(f"Auto-blocked: {source_ip[:15]}", "danger")
                
        except Exception as e:
            print(f"[ERROR] Packet spawn failed: {e}")
    
    def _classify_packet(self, source_ip):
        """Simulate packet classification (threat detection)"""
        # This simulates threat intel - in real integration, use API
        if source_ip.startswith("10.") or source_ip.startswith("192.168."):
            weights = [0.85, 0.12, 0.03]  # Mostly safe
        else:
            weights = [0.50, 0.30, 0.20]  # More suspicious
        
        return random.choices(
            [PacketType.SAFE, PacketType.SUSPICIOUS, PacketType.MALICIOUS],
            weights=weights
        )[0]
    
    def _spawn_demo_packet(self):
        """Spawn random packet for demo/testing"""
        if random.random() < Config.PACKET_SPAWN_RATE:
            ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
            self._spawn_packet(source_ip=ip)
    
    # ============================================
    # GAME LOGIC
    # ============================================
    
    def _update_game_logic(self, dt):
        """Update game state"""
        if self.state != GameState.RUNNING:
            return
        
        self.game_time += dt
        
        # Process external packets
        self._process_external_packets()
        
        # Spawn demo packets (remove this in production if using real packets)
        self._spawn_demo_packet()
        
        # Update sprites
        self.packet_sprites.update()
        self.node_sprites.update()
        
        # Check packet arrivals
        self._check_packet_arrivals()
        
        # Update threat level
        self._update_threat_level()
        
        # Update particles
        self.particle_system.update()
        
        # Check game over
        if self.network_health <= 0:
            self.state = GameState.GAME_OVER
            self.log_callback("NETWORK COMPROMISED!", "danger")
    
    def _check_packet_arrivals(self):
        """Handle packets that reached their target"""
        for packet in list(self.packet_sprites):
            if packet.reached_target and not packet.is_blocked:
                # Apply damage
                damage = packet.get_damage()
                if damage > 0:
                    self.network_health -= damage
                    self.particle_system.emit_hit_effect(packet.x, packet.y)
                    
                    if packet.packet_type == PacketType.MALICIOUS:
                        self.log_callback("MALICIOUS packet hit server!", "danger")
                
                packet.kill()
            elif packet.is_blocked:
                if packet.alpha <= 0:
                    packet.kill()
    
    def _update_threat_level(self):
        """Calculate current threat level"""
        malicious = sum(1 for p in self.packet_sprites if p.packet_type == PacketType.MALICIOUS)
        suspicious = sum(1 for p in self.packet_sprites if p.packet_type == PacketType.SUSPICIOUS)
        
        target = min(100, malicious * 20 + suspicious * 8)
        self.threat_level += (target - self.threat_level) * 0.1
    
    # ============================================
    # RENDERING
    # ============================================
    
    def _draw_background(self):
        """Draw game background and grid"""
        self.screen.fill(Config.BG_COLOR)
        
        # Draw grid in game area
        for x in range(Config.GAME_AREA_X, Config.GAME_AREA_X + Config.GAME_AREA_WIDTH, 40):
            pygame.draw.line(
                self.screen, Config.GRID_COLOR,
                (x, Config.GAME_AREA_Y),
                (x, Config.GAME_AREA_Y + Config.GAME_AREA_HEIGHT)
            )
        
        for y in range(Config.GAME_AREA_Y, Config.GAME_AREA_Y + Config.GAME_AREA_HEIGHT, 40):
            pygame.draw.line(
                self.screen, Config.GRID_COLOR,
                (Config.GAME_AREA_X, y),
                (Config.GAME_AREA_X + Config.GAME_AREA_WIDTH, y)
            )
    
    def _draw_game_area(self):
        """Draw main game area"""
        # Border
        game_rect = pygame.Rect(
            Config.GAME_AREA_X, Config.GAME_AREA_Y,
            Config.GAME_AREA_WIDTH, Config.GAME_AREA_HEIGHT
        )
        pygame.draw.rect(self.screen, Theme.NEON_BLUE, game_rect, 2)
        
        # Draw connections between nodes
        self._draw_connections()
        
        # Draw packet trails
        for packet in self.packet_sprites:
            packet.draw_trail(self.screen)
        
        # Draw sprites
        self.node_sprites.draw(self.screen)
        self.packet_sprites.draw(self.screen)
        
        # Draw particles
        self.particle_system.draw(self.screen)
    
    def _draw_connections(self):
        """Draw lines connecting network nodes"""
        # Router -> Firewall -> Server
        pygame.draw.line(
            self.screen, (40, 60, 90),
            (self.router.x, self.router.y),
            (self.firewall.x, self.firewall.y), 2
        )
        pygame.draw.line(
            self.screen, (40, 60, 90),
            (self.firewall.x, self.firewall.y),
            (self.main_server.x, self.main_server.y), 2
        )
        
        # Server -> Workstations
        for ws in self.workstations:
            pygame.draw.line(
                self.screen, (40, 60, 90),
                (self.main_server.x, self.main_server.y),
                (ws.x, ws.y), 1
            )
    
    def _draw_hud(self):
        """Draw heads-up display"""
        # Top bar background
        pygame.draw.rect(
            self.screen, Theme.PANEL_BG,
            (0, 0, Config.SCREEN_WIDTH, 50)
        )
        pygame.draw.line(
            self.screen, Theme.NEON_BLUE,
            (0, 50), (Config.SCREEN_WIDTH, 50), 2
        )
        
        # Title
        font_title = pygame.font.Font(None, 32)
        title = font_title.render("PACKET DEFENDER", True, Theme.NEON_BLUE)
        self.screen.blit(title, (20, 12))
        
        # Time
        font_time = pygame.font.Font(None, 24)
        minutes = int(self.game_time) // 60
        seconds = int(self.game_time) % 60
        time_text = font_time.render(f"TIME: {minutes:02d}:{seconds:02d}", True, Theme.TEXT_PRIMARY)
        self.screen.blit(time_text, (Config.SCREEN_WIDTH - 130, 15))
        
        # Stats summary
        stats_text = f"PROCESSED: {self.packets_processed}  |  BLOCKED: {self.packets_blocked}"
        stats_surface = font_time.render(stats_text, True, Theme.TEXT_SECONDARY)
        stats_x = (Config.SCREEN_WIDTH - stats_surface.get_width()) // 2
        self.screen.blit(stats_surface, (stats_x, 15))
    
    def _draw_control_panel(self):
        """Draw left control panel"""
        # Panel background
        panel_rect = pygame.Rect(
            Config.CONTROL_PANEL_X, Config.GAME_AREA_Y,
            Config.CONTROL_PANEL_WIDTH, 350
        )
        pygame.draw.rect(self.screen, Theme.PANEL_BG, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, Theme.NEON_PURPLE, panel_rect, 2, border_radius=8)
        
        # Title
        font = pygame.font.Font(None, 20)
        title = font.render("DEFENSE CONTROLS", True, Theme.NEON_PURPLE)
        self.screen.blit(title, (Config.CONTROL_PANEL_X + 12, Config.GAME_AREA_Y + 10))
        
        # Draw defense toggle
        self.defense_toggle.draw(self.screen)
        
        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)
    
    def _draw_ui(self):
        """Draw all UI components"""
        # HUD
        self._draw_hud()
        
        # Control panel
        self._draw_control_panel()
        
        # Health bar
        self.health_bar.set_value(self.network_health)
        self.health_bar.update()
        self.health_bar.draw(self.screen)
        
        # Threat indicator
        self.threat_indicator.set_level(self.threat_level)
        self.threat_indicator.update()
        self.threat_indicator.draw(self.screen)
        
        # Stats panel
        self.stats_panel.set_stats({
            "Packets": self.packets_processed,
            "Blocked": self.packets_blocked,
            "Active Threats": sum(1 for p in self.packet_sprites if p.packet_type == PacketType.MALICIOUS),
            "Health": f"{int(self.network_health)}%",
            "Mode": self.defense_mode
        })
        self.stats_panel.draw(self.screen)
        
        # Log panel
        self.log_panel.draw(self.screen)
    
    def _draw_pause_overlay(self):
        """Draw pause screen"""
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 28)
        
        text = font_large.render("PAUSED", True, Theme.NEON_YELLOW)
        text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        hint = font_small.render("Press SPACE or click PAUSE to resume", True, Theme.TEXT_SECONDARY)
        hint_rect = hint.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(hint, hint_rect)
    
    def _draw_game_over(self):
        """Draw game over screen"""
        overlay = pygame.Surface((Config.SCREEN_WIDTH, Config.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((50, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 72)
        font_small = pygame.font.Font(None, 28)
        
        text = font_large.render("NETWORK COMPROMISED", True, Theme.NEON_RED)
        text_rect = text.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        stats = font_small.render(
            f"Packets Processed: {self.packets_processed}  |  Blocked: {self.packets_blocked}",
            True, Theme.TEXT_PRIMARY
        )
        stats_rect = stats.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(stats, stats_rect)
        
        hint = font_small.render("Press R to restart or ESC to quit", True, Theme.TEXT_SECONDARY)
        hint_rect = hint.get_rect(center=(Config.SCREEN_WIDTH // 2, Config.SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(hint, hint_rect)
    
    # ============================================
    # INPUT HANDLING
    # ============================================
    
    def _handle_events(self):
        """Handle all pygame events"""
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self._action_toggle_pause()
                elif event.key == pygame.K_r and self.state == GameState.GAME_OVER:
                    self._restart_game()
                elif event.key == pygame.K_a:
                    self.defense_toggle.toggle()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_clicked = True
                    self._handle_click(mouse_pos)
        
        # Update buttons
        for button in self.buttons:
            button.update(mouse_pos, mouse_pressed)
        
        # Update defense toggle
        self.defense_toggle.update(mouse_pos, mouse_clicked)
    
    def _handle_click(self, pos):
        """Handle mouse click on game area"""
        # Check if clicked on a packet
        for packet in self.packet_sprites:
            if packet.contains_point(pos):
                if packet.packet_type in [PacketType.SUSPICIOUS, PacketType.MALICIOUS]:
                    packet.block()
                    self.packets_blocked += 1
                    self.particle_system.emit_block_effect(packet.x, packet.y)
                    self.block_callback(packet.source_ip)
                    self.log_callback(f"Manually blocked: {packet.source_ip[:15]}", "warning")
                break
    
    def _restart_game(self):
        """Restart the game"""
        self.network_health = Config.MAX_HEALTH
        self.packets_processed = 0
        self.packets_blocked = 0
        self.threat_level = 0
        self.game_time = 0
        self.blocked_ips.clear()
        self.packet_sprites.empty()
        self.state = GameState.RUNNING
        self.log_panel.clear_logs()
        self.log_callback("Game restarted", "success")
    
    # ============================================
    # MAIN LOOP
    # ============================================
    
    def run(self):
        """Main game loop"""
        print("[OK] Starting game loop...")
        self.log_callback("Monitoring network traffic...", "info")
        
        try:
            while self.running:
                # Calculate delta time
                dt = self.clock.tick(Config.FPS) / 1000.0
                
                # Handle input
                self._handle_events()
                
                # Update game logic
                self._update_game_logic(dt)
                
                # Render
                self._draw_background()
                self._draw_game_area()
                self._draw_ui()
                
                # Draw overlays based on state
                if self.state == GameState.PAUSED:
                    self._draw_pause_overlay()
                elif self.state == GameState.GAME_OVER:
                    self._draw_game_over()
                
                # Update display
                pygame.display.flip()
                
        except Exception as e:
            print(f"[ERROR] Game loop error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self._cleanup()
    
    def _cleanup(self):
        """Clean up resources"""
        print("[OK] Shutting down...")
        pygame.quit()
    
    # ============================================
    # EXTERNAL INTERFACE
    # ============================================
    
    def get_blocked_ips(self):
        """Return blocked IPs for firewall module"""
        return self.blocked_ips.copy()
    
    def get_stats(self):
        """Return current game statistics"""
        return {
            "health": self.network_health,
            "packets_processed": self.packets_processed,
            "packets_blocked": self.packets_blocked,
            "threat_level": self.threat_level,
            "defense_mode": self.defense_mode,
            "game_time": self.game_time,
            "state": self.state.value
        }
    
    def inject_packet(self, source_ip, packet_type="malicious"):
        """External method to inject a packet (for testing)"""
        self._spawn_packet(source_ip=source_ip, packet_type=packet_type)


# ============================================
# ENTRY POINT
# ============================================

def main():
    """Main entry point"""
    print("=" * 50)
    print("  PACKET DEFENDER - Cyber Defense Simulation")
    print("=" * 50)
    print()
    
    # Create game instance
    # In production, pass real queue and callbacks:
    # game = CyberDefenseGame(
    #     packet_queue=shared_packet_queue,
    #     log_callback=logger.log,
    #     block_callback=firewall.block_ip
    # )
    
    game = CyberDefenseGame()
    game.run()


if __name__ == "__main__":
    main()
