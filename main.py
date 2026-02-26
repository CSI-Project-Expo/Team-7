"""
===========================================================
PACKET DEFENDER - Main Entry Point
===========================================================
Complete Pygame implementation of Packet Defender.
Includes all requested features:
- Menu, Briefing, Report, Victory, Game Over screens
- 3 Waves (15s, 20s, 30s)
- Firewall & Server Configuration Panel
- Manual Click-to-Block & Auto-Defense Modes
- Resource Management (CPU/RAM)
- Attack Encyclopedia with detailed info
===========================================================
"""

import pygame
import random
import math
import time
import threading
from queue import Queue, Empty

# Import Sprites
from sprites import (
    PacketSprite, PacketType, NetworkNode, 
    ConnectionAnimator, ParticleSystem,
    BoosterSprite, BoosterType,
    IntelSprite, IntelType
)

# Import Firewall Logic
from firewall import DefenseEngine, AttackDatabase

# Import UI Components
from ui_components import (
    Theme, MenuScreen, HealthBar, StatsPanel, LogPanel,
    ThreatIndicator, DefenseModeToggle, WaveProgressBar,
    LiveTerminalFeed, SmartSuggestionBar, MissionBriefing,
    PostWaveReport, AttackEncyclopedia, DefensePanel,
    AttackPopup, DefenseBar, CyberButton, safe_color,
    ControlPanel, ActionButtonGroup, VictoryReport,
    AchievementNotification, GameOverReport, AdaptiveThreatIndicator
)

# Import Sniffer
from packet_sniffer import PacketSniffer

# Import Logger
from logger import log_event, EventType

# ═══════════════════════════════════════════════
#  CONFIGURATION & CONSTANTS
# ═══════════════════════════════════════════════

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
FPS = 60

WAVES = [
    {"num": 1, "name": "Initial Probe", "duration": 30, "attacks": ["PORT_SCAN", "PING_FLOOD", "BRUTE_FORCE"], "hint": "Check filters to enable rules.", "spawn_rate": 1.2, "hostile_ratio": 0.3},
    {"num": 2, "name": "Coordinated Strike", "duration": 30, "attacks": ["SYN_FLOOD", "BRUTE_FORCE", "SQL_INJECTION"], "hint": "SYN Cookies are critical.", "spawn_rate": 3.0, "hostile_ratio": 0.45},
    {"num": 3, "name": "Advanced Threat", "duration": 30, "attacks": ["DDOS", "MALWARE", "DNS_SPOOF", "SYN_FLOOD"], "hint": "Enable all rules!", "spawn_rate": 4.2, "hostile_ratio": 0.6}
]

class PacketDefender:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Packet Defender - Cyber Security")
        self.clock = pygame.time.Clock()
        self.running = True
        self.paused = False
        self.state = "MENU"
        self.current_wave_idx = 0
        self.health = 100
        self.score = 0
        self.high_score = self.load_high_score()
        self.heals_remaining = 5
        self.packets_blocked = 0
        self.packets_leaked = 0
        self.intel_collected = 0
        self.auto_defense = False
        self.score_multiplier = 1
        self.multiplier_timer = 0
        self.slow_timer = 0
        self.auto_block_timer = 0
        self.cpu_usage = 0.0
        self.ram_usage = 0.0
        self.max_cpu = 100.0
        
        self.defense_engine = DefenseEngine()
        self.sniffer = PacketSniffer(simulation_mode=True)
        self.sniffer.start()
        
        self.all_sprites = pygame.sprite.Group()
        self.packets = pygame.sprite.Group()
        self.nodes = pygame.sprite.Group()
        self.boosters = pygame.sprite.Group()
        self.intel_items = pygame.sprite.Group()
        self.particles = ParticleSystem()
        
        self.ui_menu = MenuScreen(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_briefing = MissionBriefing(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_report = PostWaveReport(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_health = HealthBar(SCREEN_WIDTH//2 - 320, 40, 200, 25, 100)
        self.ui_threat = ThreatIndicator(SCREEN_WIDTH//2 + 120, 40, 200, 45)
        self.ui_progress = WaveProgressBar(SCREEN_WIDTH//2 - 150, 10, 300, 20)
        self.ui_stats = StatsPanel(SCREEN_WIDTH - 220, 20, 200, 160)
        self.ui_defense_bar = DefenseBar(SCREEN_WIDTH - 220, 190, 200, 60, self.toggle_firewall_panel)
        self.ui_toggle = DefenseModeToggle(SCREEN_WIDTH - 220, 260, 200, 30, self.set_auto_defense)
        self.ui_terminal = LiveTerminalFeed(260, SCREEN_HEIGHT - 160, 680, 140)
        self.ui_log = LogPanel(SCREEN_WIDTH - 220, 300, 200, 220)
        self.ui_suggestion = SmartSuggestionBar()
        self.ui_firewall = DefensePanel(200, 50, 800, 600, self.defense_engine, self.on_rule_toggle)
        self.ui_encyclopedia = AttackEncyclopedia(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_popup = AttackPopup(self.defense_engine)
        self.ui_notify = AchievementNotification(SCREEN_WIDTH)
        self.ui_adaptive = AdaptiveThreatIndicator(SCREEN_WIDTH)
        self.ui_game_over = GameOverReport(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_victory = VictoryReport(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.ui_control = ControlPanel(10, 10, 240, SCREEN_HEIGHT - 20, self.set_auto_defense, self.toggle_encyclopedia, self.toggle_firewall_panel)
        self.ui_actions = ActionButtonGroup(SCREEN_WIDTH//2 - 110, SCREEN_HEIGHT - 210, 225, 40, self.manual_block, self.clear_all_packets, self.heal_server)
        self.score_font = pygame.font.Font(None, 42)
        self.setup_network()
        self.wave_timer = 0
        self.last_spawn_time = 0
        self.last_suggestion_time = 0
        self.last_booster_spawn = 0
        self.last_collectible_spawn = 0
        self.wave_damage_taken = 0
        self.wave_packets_blocked = 0

    def load_high_score(self):
        try:
            import json
            with open("scores.json", "r") as f:
                data = json.load(f)
                if data: return max(item["score"] for item in data)
        except: pass
        return 0

    def save_score(self):
        try:
            import json
            from datetime import datetime
            new_entry = {"score": self.score, "wave": self.current_wave_idx + 1, "date": datetime.now().strftime("%Y-%m-%d %H:%M")}
            try:
                with open("scores.json", "r") as f: data = json.load(f)
            except: data = []
            data.append(new_entry); 
            with open("scores.json", "w") as f: json.dump(data, f, indent=2)
            if self.score > self.high_score: self.high_score = self.score
        except: pass

    def setup_network(self):
        self.node_ws = NetworkNode(320, 350, NetworkNode.WORKSTATION, "WS")
        self.node_router = NetworkNode(480, 350, NetworkNode.ROUTER, "R")
        self.node_fw = NetworkNode(640, 350, NetworkNode.FIREWALL, "FW")
        self.node_server = NetworkNode(880, 350, NetworkNode.SERVER, "SRV")
        self.nodes.add(self.node_ws, self.node_router, self.node_fw, self.node_server)
        self.connections = ConnectionAnimator()
        self.connections.set_connections([(self.node_ws, self.node_router, (60,70,90)), (self.node_router, self.node_fw, (60,70,90)), (self.node_fw, self.node_server, (60,70,90))])
        self.ui_suggestion.set_position(640, 300)

    def set_auto_defense(self, state):
        self.auto_defense = state; self.ui_control.auto_defense = state; self.ui_toggle.set_state(state)

    def toggle_encyclopedia(self):
        self.ui_encyclopedia.toggle()
        # Game should be paused if either panel is visible
        self.paused = self.ui_encyclopedia.visible or self.ui_firewall.visible

    def toggle_firewall_panel(self):
        self.ui_firewall.toggle_visible()
        # Game should be paused if either panel is visible
        self.paused = self.ui_encyclopedia.visible or self.ui_firewall.visible

    def on_rule_toggle(self, rid, state): pass

    def manual_block(self):
        count = 0
        for p in self.packets:
            if p.is_hostile() and not p.is_blocked: 
                p.block("MANUAL"); count += 1
        if count > 0: 
            self.cpu_usage = min(100.0, self.cpu_usage + count * 2.0)
            msg = f"MANUAL INTERVENTION: Blocked {count} packets"
            self.ui_terminal.add_entry(msg, "blocked")
            log_event(EventType.BLOCK.value, msg)

    def clear_all_packets(self):
        count = len(self.packets)
        self.packets.empty()
        self.ui_log.add_log(f"NETWORK PURGE: {count} pkts", "danger")
        log_event(EventType.SYSTEM.value, f"Network Purge Executed: Dropped {count} packets")

    def heal_server(self):
        if self.heals_remaining > 0: self.health = min(100, self.health + 25); self.heals_remaining -= 1

    def reset_game(self):
        """Safely reset game state for replay without re-init sniffer/display"""
        self.current_wave_idx = 0
        self.health = 100
        self.score = 0
        self.heals_remaining = 5
        self.packets_blocked = 0
        self.packets_leaked = 0
        self.intel_collected = 0
        self.paused = False
        self.auto_defense = False
        self.cpu_usage = 0.0
        self.ram_usage = 0.0
        self.wave_timer = 0
        self.last_spawn_time = 0
        self.wave_damage_taken = 0
        self.wave_packets_blocked = 0
        
        self.packets.empty()
        self.boosters.empty()
        self.intel_items.empty()
        self.particles.clear()
        self.ui_log.clear_logs()
        self.ui_terminal.clear()
        self.ui_health.set_value(100)
        self.ui_toggle.set_state(False)
        self.ui_control.auto_defense = False
        self.defense_engine.reset()
        log_event(EventType.SYSTEM.value, "SYSTEM REBOOT COMPLETE - ALL SYSTEMS NOMINAL")
        self.start_briefing()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mpos = event.pos
                if event.button == 1: # Left Click
                    self.process_click(mpos)
                elif event.button == 4: # Scroll Up
                    if self.ui_firewall.visible: self.ui_firewall.handle_scroll(1)
                    if self.ui_log.rect.collidepoint(mpos): self.ui_log.scroll = max(0, self.ui_log.scroll - 1)
                    if self.ui_terminal.rect.collidepoint(mpos): self.ui_terminal.scroll = max(0, self.ui_terminal.scroll - 1)
                elif event.button == 5: # Scroll Down
                    if self.ui_firewall.visible: self.ui_firewall.handle_scroll(-1)
                    if self.ui_log.rect.collidepoint(mpos): self.ui_log.scroll = min(max(0, len(self.ui_log.logs)-1), self.ui_log.scroll + 1)
                    if self.ui_terminal.rect.collidepoint(mpos): self.ui_terminal.scroll = min(max(0, len(self.ui_terminal.lines)-1), self.ui_terminal.scroll + 1)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.ui_firewall.visible: self.toggle_firewall_panel()
                    elif self.ui_encyclopedia.visible: self.toggle_encyclopedia()
                    else: self.running = False
                
                if self.state == "MENU":
                    if self.ui_menu.handle_key(event.key) == "START": self.start_briefing()
                elif self.state == "BRIEFING":
                    if self.ui_briefing.handle_key(event.key): self.start_wave()
                elif self.state == "PLAYING":
                    # Only allow manual pause toggle if no menus are open
                    if event.key == pygame.K_SPACE:
                        if not (self.ui_firewall.visible or self.ui_encyclopedia.visible):
                            self.paused = not self.paused
                            
                    if event.key == pygame.K_f: self.toggle_firewall_panel()
                    if event.key == pygame.K_i: self.toggle_encyclopedia()
                    if event.key == pygame.K_a: self.set_auto_defense(not self.auto_defense)
                    
                    if not self.paused:
                        if event.key == pygame.K_q: self.manual_block()
                        if event.key == pygame.K_e: self.heal_server()
                        if event.key == pygame.K_c: self.clear_all_packets()
                elif self.state in ["VICTORY", "GAME_OVER"] and event.key == pygame.K_r: self.reset_game()

    def process_click(self, mpos):
        if self.state == "MENU":
            res = self.ui_menu.handle_click(mpos)
            if res == "START": self.start_briefing()
            elif res == "QUIT": self.running = False
        elif self.state == "BRIEFING":
            if self.ui_briefing.handle_click(mpos): self.start_wave()
        elif self.state == "REPORT":
            if self.ui_report.handle_click(mpos): self.next_wave()
        elif self.state == "PLAYING":
            # 1. Panels (Full-screen or modal)
            if self.ui_encyclopedia.visible:
                if self.ui_encyclopedia.handle_click(mpos):
                    self.paused = self.ui_encyclopedia.visible or self.ui_firewall.visible
            elif self.ui_firewall.visible:
                if self.ui_firewall.handle_click(mpos):
                    self.paused = self.ui_encyclopedia.visible or self.ui_firewall.visible
            else:
                # 2. UI HUD elements (Buttons take priority)
                if self.ui_control.handle_click(mpos): return
                if self.ui_actions.handle_click(mpos): return
                if self.ui_defense_bar.handle_click(mpos): return
                if self.ui_toggle.handle_click(mpos): return
                
                # 3. Game objects (Intel, Boosters, Packets)
                for c in self.intel_items:
                    if c.contains_point(mpos): self.score += c.points * self.score_multiplier; self.intel_collected += 1; c.kill(); self.particles.emit_success_effect(mpos[0], mpos[1]); return
                for b in self.boosters:
                    if b.contains_point(mpos): self.apply_booster(b); b.kill(); self.particles.emit_success_effect(mpos[0], mpos[1]); return
                for p in self.packets:
                    if p.contains_point(mpos) and p.is_hostile() and not p.is_blocked:
                        p.block("MANUAL")
                        self.score += 20 * self.score_multiplier
                        self.packets_blocked += 1
                        self.wave_packets_blocked += 1
                        self.particles.emit_success_effect(p.x, p.y)
                        self.cpu_usage = min(100.0, self.cpu_usage + 5.0)
                        
                        # Terminal Logging
                        msg = f"MANUAL BLOCK: {p.threat_name} from {p.source_ip}"
                        self.ui_terminal.add_entry(msg, "blocked")
                        log_event(EventType.BLOCK.value, msg)
                        return
        elif self.state == "VICTORY":
            res = self.ui_victory.handle_click(mpos)
            if res == "RESET": self.reset_game()
            elif res == "QUIT": self.running = False
        elif self.state == "GAME_OVER":
            res = self.ui_game_over.handle_click(mpos)
            if res == "REPLAY": self.reset_game()
            elif res == "QUIT": self.running = False

    def apply_booster(self, b):
        if b.btype == BoosterType.HEAL:
            self.health = min(100, self.health + 15)
            self.ui_log.add_log(f"Network Heal: +15 HP", "success")
            log_event(EventType.SYSTEM.value, f"Network Heal: +15 HP ({self.health} left)")
        elif b.btype == BoosterType.DOUBLE_SCORE:
            self.score_multiplier = 2; self.multiplier_timer = 600
            self.ui_log.add_log("2X Score Active!", "rule")
            log_event(EventType.SYSTEM.value, "2X Score Multiplier Active!")
        elif b.btype == BoosterType.PURGE:
            self.clear_all_packets()
        elif b.btype == BoosterType.SLOW_MO:
            self.slow_timer = 300
            self.ui_log.add_log("Slow-Mo Engaged", "warning")
            log_event(EventType.SYSTEM.value, "Slow-Mo Mode Engaged")
        elif b.btype == BoosterType.AUTO_BLOCK:
            self.auto_block_timer = 180
            self.ui_log.add_log("Auto-Block Satellite ONLINE", "rule")
            log_event(EventType.SYSTEM.value, "Auto-Block Satellite Online")

    def start_briefing(self):
        if self.current_wave_idx < len(WAVES): 
            self.state = "BRIEFING"; self.ui_briefing.show(WAVES[self.current_wave_idx])
            self.ui_log.add_log(f"Mission: {WAVES[self.current_wave_idx]['name']}", "info")

    def start_wave(self):
        self.state = "PLAYING"; self.health = 100; self.packets.empty(); wave = WAVES[self.current_wave_idx]
        self.wave_timer = wave["duration"] * FPS; self.wave_damage_taken = 0; self.wave_packets_blocked = 0
        self.ui_log.add_log(f"WAVE {wave['num']} STARTED", "warning")

    def next_wave(self):
        self.current_wave_idx += 1
        if self.current_wave_idx < len(WAVES): self.start_briefing()
        else: self.state = "VICTORY"; self.ui_log.add_log("NETWORK SECURED!", "success")

    def spawn_packet(self):
        if len(self.packets) > 100: return # Hard safety limit to prevent explosion
        now = pygame.time.get_ticks(); wave = WAVES[self.current_wave_idx]
        if (wave["duration"] * FPS - self.wave_timer) / FPS < 2.0: return
        prog = 1.0 - (self.wave_timer / (wave["duration"] * FPS))
        rate = wave["spawn_rate"] * (1.0 + prog)
        if now - self.last_spawn_time > (1000 / rate):
            self.last_spawn_time = now
            if random.random() < wave["hostile_ratio"] * (1.0 + prog * 0.5):
                ptype = random.choice([PacketType.SUSPICIOUS, PacketType.MALICIOUS]); attack_id = random.choice(wave["attacks"])
            else: ptype = PacketType.SAFE; attack_id = "SAFE"
            p = PacketSprite(0, 350 + random.randint(-50, 50), self.node_router.x, self.node_router.y, ptype)
            if attack_id != "SAFE":
                info = AttackDatabase.get(attack_id)
                if info:
                    p.attack_id = attack_id; p.threat_name = info["name"]; p.recolor(info["color"])
                    p.threat_severity = info["severity"]; p.threat_damage = info["damage"]
                    p.source_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
            self.packets.add(p)

    def spawn_booster(self):
        if random.random() > 0.15: return # Further throttle booster spawning
        bx, by = random.randint(300, 900), random.randint(100, 400); btype = random.choice([BoosterType.HEAL, BoosterType.DOUBLE_SCORE, BoosterType.PURGE, BoosterType.SLOW_MO, BoosterType.AUTO_BLOCK])
        self.boosters.add(BoosterSprite(bx, by, btype))

    def spawn_collectible(self):
        cx = random.randint(300, 900); itype = IntelType.LARGE if random.random() < 0.2 else IntelType.STANDARD
        self.intel_items.add(IntelSprite(cx, itype))

    def pull_sniffer_packets(self):
        if len(self.packets) > 100: return
        # Limit packets pulled per frame to prevent lag spikes
        max_pull = 5 # Reduced from 10
        count = 0
        while not self.sniffer.is_queue_empty() and count < max_pull:
            p_data = self.sniffer.get_packet()
            if not p_data: break
            # Only spawn some of the sniffed packets to reduce load
            if random.random() < 0.3:
                ps = PacketSprite(0, 350 + random.randint(-40, 40), self.node_router.x, self.node_router.y, PacketType.SUSPICIOUS, ip=p_data.src_ip)
                self.packets.add(ps)
            count += 1

    def update(self):
        if self.state == "MENU": self.ui_menu.update(); return
        if self.state == "BRIEFING":
            self.ui_briefing.update()
            if not self.ui_briefing.visible: self.start_wave()
            return
        if self.state == "REPORT":
            self.ui_report.update()
            if not self.ui_report.visible: self.next_wave()
            return
        if self.state == "VICTORY":
            self.ui_victory.update()
            return
            
        # UI updates that should run even when paused
        self.ui_toggle.update()
        self.ui_actions.update(pygame.mouse.get_pos(), pygame.mouse.get_pressed())
        self.ui_defense_bar.update(self.defense_engine, pygame.mouse.get_pos())
        self.ui_firewall.update(pygame.mouse.get_pos())
        self.ui_health.update()
        self.ui_threat.update()
        
        if self.paused or self.state != "PLAYING": return
        
        if self.wave_timer > 0:
            self.wave_timer -= 1
            if self.wave_timer <= 0: 
                self.end_wave()
                self.ui_log.add_log(f"WAVE COMPLETE", "success")
            
        if self.auto_defense:
            self.cpu_usage = min(100.0, self.cpu_usage + 0.12)
            if self.cpu_usage >= 100.0: 
                self.set_auto_defense(False)
                self.ui_notify.show("CPU OVERHEAT", color=Theme.NEON_RED)
                self.ui_log.add_log("CPU OVERHEAT - AUTO OFF", "danger")
        else:
            self.cpu_usage = max(0.0, self.cpu_usage - 0.2)
            
        self.ram_usage = min(100.0, (len(self.packets) / 40.0) * 100.0)
        self.spawn_packet()
        
        if random.random() < 0.005: self.spawn_booster()
        if random.random() < 0.01: self.spawn_collectible()
        
        self.pull_sniffer_packets()
        self.nodes.update()
        self.particles.update()
        self.connections.update()
        self.boosters.update()
        self.intel_items.update(0.4 if self.slow_timer > 0 else 1.0)
        self.ui_notify.update()
        self.ui_adaptive.update()
        
        if self.multiplier_timer > 0: self.multiplier_timer -= 1
        if self.slow_timer > 0: self.slow_timer -= 1
        if self.auto_block_timer > 0: self.auto_block_timer -= 1
        
        p_scale = 0.4 if self.slow_timer > 0 else 1.0
        for p in self.packets:
            p.update(p_scale)
            if p.reached_target and not p.is_blocked:
                if p.target_x == self.node_router.x:
                    p.target_x, p.target_y = self.node_fw.x, self.node_fw.y
                    p.vx = (p.target_x - p.x) / 30
                    p.vy = (p.target_y - p.y) / 30
                    p.reached_target = False
                elif p.target_x == self.node_fw.x:
                    blocked, rule_name, info, eff = self.defense_engine.inspect_packet(p.attack_id, p.source_ip)
                    
                    # If auto-defense mode is ON, it can block even if rules are disabled
                    is_auto_mode = self.auto_defense or self.auto_block_timer > 0
                    if is_auto_mode and p.is_hostile() and not blocked:
                        blocked = True
                        rule_name = "AUTO-SYSTEM"
                        eff = 1.0
                    
                    if blocked:
                        p.block(rule_name)
                        self.score += int(15 * eff * self.score_multiplier)
                        self.packets_blocked += 1
                        self.wave_packets_blocked += 1
                        self.particles.emit_success_effect(p.x, p.y)
                        self.node_fw.trigger_block()
                        self.connections.flash_block(self.node_router, self.node_fw)
                        
                        # LOG TO TERMINAL (#28)
                        msg = f"BLOCK: {p.threat_name} from {p.source_ip} using {rule_name}"
                        self.ui_terminal.add_entry(msg, "blocked")
                        log_event(EventType.BLOCK.value, msg)
                    else:
                        if p.is_hostile():
                            # Attack passed firewall - log why
                            missing = rule_name if rule_name else "No countermeasure"
                            msg = f"ALERT: {p.threat_name} from {p.source_ip} - RULE DISABLED [{missing}]"
                            self.ui_terminal.add_entry(msg, "critical")
                            self.ui_terminal.add_entry(">>> MANUAL INTERVENTION REQUIRED!", "warning")
                            self.ui_log.add_log(f"ALERT: {p.threat_name} Bypassed FW", "danger")
                            log_event(EventType.ATTACK.value, f"{p.threat_name} bypassed firewall (Rule: {missing})")
                        
                        p.target_x, p.target_y = self.node_server.x, self.node_server.y
                        p.vx = (p.target_x - p.x) / 40
                        p.vy = (p.target_y - p.y) / 40
                        p.reached_target = False
                elif p.target_x == self.node_server.x:
                    if p.is_hostile():
                        dmg = p.get_damage()
                        self.health -= dmg
                        self.wave_damage_taken += dmg
                        self.packets_leaked += 1
                        self.node_server.trigger_hit()
                        self.connections.flash_hit(self.node_fw, self.node_server)
                        self.particles.emit_hit_effect(p.x, p.y)
                        if self.health < 30: self.ui_log.add_log("CRITICAL HEALTH!", "danger")
                    p.kill()
            if p.is_blocked and p.alpha <= 0: p.kill()
            
        if self.health <= 0: 
            self.state = "GAME_OVER"
            self.ui_log.add_log("GAME OVER - NETWORK BREACHED", "danger")
            self.save_score()
            self.ui_game_over.show(self.score, self.packets_blocked, self.packets_leaked)
            
        self.ui_health.set_value(self.health)
        self.ui_threat.set_level(sum(1 for p in self.packets if p.is_hostile()) * 10)
        
        wave = WAVES[self.current_wave_idx]
        self.ui_progress.set_wave(wave["num"], wave["name"], 1.0 - (self.wave_timer / (wave["duration"] * FPS)))
        self.ui_stats.set_stats({
            "Score": self.score, 
            "Hi-Score": self.high_score, 
            "CPU": f"{int(self.cpu_usage)}%", 
            "RAM": f"{int(self.ram_usage)}%", 
            "Wave": self.current_wave_idx + 1
        })


    def end_wave(self):
        if self.current_wave_idx >= len(WAVES) - 1: 
            self.state = "VICTORY"
            self.save_score()
            self.ui_victory.show(self.score, self.high_score, self.packets_blocked, self.packets_leaked, self.intel_collected)
        else:
            self.state = "REPORT"
            self.ui_report.show({"wave_num": self.current_wave_idx + 1, "damage_taken": self.wave_damage_taken, "blocked": self.wave_packets_blocked, "intel": self.intel_collected, "rules_active": self.defense_engine.active_count(), "wave_score": 100*(self.current_wave_idx+1), "best_rule": "N/A"})

    def draw(self):
        if self.state == "MENU": self.ui_menu.draw(self.screen); pygame.display.flip(); return
        self.screen.fill((10, 15, 25))
        for x in range(0, SCREEN_WIDTH, 40): pygame.draw.line(self.screen, (20, 25, 35), (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, 40): pygame.draw.line(self.screen, (20, 25, 35), (0, y), (SCREEN_WIDTH, y))
        self.connections.draw(self.screen)
        for p in self.packets: p.draw_trail(self.screen)
        self.packets.draw(self.screen); self.nodes.draw(self.screen); self.boosters.draw(self.screen); self.intel_items.draw(self.screen); self.particles.draw(self.screen)
        self.ui_health.draw(self.screen); self.ui_threat.draw(self.screen); self.ui_progress.draw(self.screen); self.ui_stats.draw(self.screen); self.ui_defense_bar.draw(self.screen); self.ui_toggle.draw(self.screen); self.ui_terminal.draw(self.screen); self.ui_log.draw(self.screen); self.ui_suggestion.draw(self.screen); self.ui_notify.draw(self.screen); self.ui_adaptive.draw(self.screen); self.ui_control.draw(self.screen); self.ui_actions.draw(self.screen)
        
        if self.state in ["PLAYING", "BRIEFING", "REPORT"]:
            score_t = self.score_font.render(f"SCORE: {self.score}", True, (255, 220, 0))
            self.screen.blit(score_t, (SCREEN_WIDTH//2 - score_t.get_width()//2, 45))

        if self.state == "BRIEFING": self.ui_briefing.draw(self.screen)
        elif self.state == "REPORT": self.ui_report.draw(self.screen)
        elif self.state == "VICTORY": self.ui_victory.draw(self.screen)
        elif self.state == "GAME_OVER": self.ui_game_over.draw(self.screen)
        # Draw panels
        self.ui_firewall.draw(self.screen)
        self.ui_encyclopedia.draw(self.screen)
        
        # Only show the PAUSED overlay if the game is manually paused AND no menus are open
        if self.paused and not (self.ui_firewall.visible or self.ui_encyclopedia.visible):
            self.draw_overlay("PAUSED", Theme.NEON_YELLOW, "Press [SPACE] to resume")
            
        pygame.display.flip()

    def draw_overlay(self, title, color, subtext):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); self.screen.blit(overlay, (0, 0))
        font_t = pygame.font.Font(None, 72); font_s = pygame.font.Font(None, 32); tt = font_t.render(title, True, color); st = font_s.render(subtext, True, Theme.TEXT_PRIMARY)
        self.screen.blit(tt, (SCREEN_WIDTH//2 - tt.get_width()//2, 250)); self.screen.blit(st, (SCREEN_WIDTH//2 - st.get_width()//2, 330))

    def run(self):
        try:
            while self.running: 
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            import traceback
            error_msg = f"CRITICAL SYSTEM CRASH: {str(e)}"
            log_event(EventType.ERROR.value, error_msg)
            with open("crash_report.txt", "w") as f:
                f.write(error_msg + "\n")
                f.write(traceback.format_exc())
            print(f"\n[FATAL] Game crashed! Error logged to crash_report.txt")
        finally:
            self.sniffer.stop()
            self.defense_engine.cleanup()
            pygame.quit()

if __name__ == "__main__":
    game = PacketDefender(); game.run()
