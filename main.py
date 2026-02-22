"""
===========================================================
PACKET DEFENDER - ULTIMATE CYBER DEFENSE SIMULATION
===========================================================
ALL FEATURES INCLUDED:
- Voice Alerts
- Wave System + Boss Battles
- Score + Combo + Achievements
- World Map + Live Graph + Attack DNA
- Power-ups
- AI Threat Predictor (NEW!)
- Hacker Chat Interceptor (NEW!)
- Network Heartbeat Monitor (NEW!)
- Cyber News Ticker (NEW!)
- Attack Fingerprint (NEW!)
===========================================================
"""

import pygame
import sys
import random
import math
from queue import Queue, Empty
from enum import Enum

# Core modules
try:
    from sprites import PacketSprite, NetworkNode, ParticleSystem, PacketType
    from ui_components import (HealthBar, CyberButton, StatsPanel, LogPanel, 
                               ThreatIndicator, DefenseModeToggle, Theme)
    print("[OK] Core modules")
except ImportError as e:
    print(f"[ERROR] Core: {e}")
    sys.exit(1)

# Voice
try:
    from voice_alert import VoiceAlert
    VOICE = True
except:
    VOICE = False
print(f"[{'OK' if VOICE else 'NO'}] Voice")

# Enhancements
try:
    from game_enhancements import WaveSystem, ScoreSystem, AchievementSystem, EndGameReport
    ENHANCE = True
except:
    ENHANCE = False
print(f"[{'OK' if ENHANCE else 'NO'}] Enhancements")

# Advanced
try:
    from advanced_features import MiniWorldMap, LiveThreatGraph, BossSystem, PowerUpSystem, AttackDNA
    ADVANCED = True
except:
    ADVANCED = False
print(f"[{'OK' if ADVANCED else 'NO'}] Advanced")

# Unique features
try:
    from unique_features import (AIThreatPredictor, HackerChatInterceptor, 
                                  NetworkHeartbeat, CyberNewsTicker, AttackFingerprint)
    UNIQUE = True
except:
    UNIQUE = False
print(f"[{'OK' if UNIQUE else 'NO'}] Unique")


class Config:
    WIDTH = 1200
    HEIGHT = 700
    FPS = 60
    TITLE = "PACKET DEFENDER - Ultimate Edition"
    GAME_X, GAME_Y = 250, 80
    GAME_W, GAME_H = 700, 560
    SIDE_X, SIDE_W = 960, 235
    CTRL_X, CTRL_W = 5, 240
    MAX_HP = 100
    MAX_PKT = 80
    BG = (8, 12, 20)
    GRID = (20, 30, 45)


class State(Enum):
    RUN = 1
    PAUSE = 2
    OVER = 3
    BOSS = 4


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption(Config.TITLE)
        self.clock = pygame.time.Clock()
        
        self.state = State.RUN
        self.running = True
        self.time = 0
        self.hp = Config.MAX_HP
        self.wave_hp = Config.MAX_HP
        self.pkts = 0
        self.blocked = 0
        self.threat = 0
        self.mode = "MANUAL"
        self.blocked_ips = set()
        
        self.packets = pygame.sprite.Group()
        self.nodes = pygame.sprite.Group()
        self.particles = ParticleSystem()
        
        self.fonts = {
            'L': pygame.font.Font(None, 48),
            'M': pygame.font.Font(None, 28),
            'S': pygame.font.Font(None, 20),
            'T': pygame.font.Font(None, 16)
        }
        
        self.popup_ach = None
        self.popup_ach_t = 0
        self.popup_pwr = None
        self.popup_pwr_t = 0
        self.combo_t = 0
        self.combo_v = 0
        self.boss_warn = 0
        
        self._init_systems()
        self._init_nodes()
        self._init_ui()
        self._init_unique()
        
        if self.voice:
            self.voice.alert_game_start()
        if self.waves:
            self.waves.start_game()
        
        print("[OK] Game ready!")
    
    def _init_systems(self):
        self.voice = VoiceAlert() if VOICE else None
        
        if ENHANCE:
            self.waves = WaveSystem()
            self.waves.on_wave_start = self._wave_start
            self.waves.on_wave_complete = self._wave_end
            self.score = ScoreSystem()
            self.score.on_combo_change = self._combo
            self.achieve = AchievementSystem()
            self.achieve.on_achievement_unlock = self._ach
            self.report = EndGameReport()
        else:
            self.waves = self.score = self.achieve = self.report = None
        
        if ADVANCED:
            self.boss = BossSystem()
            self.boss.on_boss_spawn = self._boss_spawn
            self.boss.on_boss_defeated = self._boss_dead
            self.boss.on_boss_attack = self._boss_atk
            self.powerups = PowerUpSystem()
            self.powerups.on_powerup_collect = self._pwr
            self.worldmap = MiniWorldMap(Config.CTRL_X, 430, Config.CTRL_W, 100)
            self.graph = LiveThreatGraph(Config.SIDE_X, 440, Config.SIDE_W, 80)
            self.dna = AttackDNA(Config.SIDE_X, 530, Config.SIDE_W, 70)
        else:
            self.boss = self.powerups = self.worldmap = self.graph = self.dna = None
    
    def _init_unique(self):
        if UNIQUE:
            self.ai_pred = AIThreatPredictor(Config.CTRL_X, 540, Config.CTRL_W, 105)
            self.hacker_chat = HackerChatInterceptor(Config.SIDE_X, 610, Config.SIDE_W, 85)
            self.heartbeat = NetworkHeartbeat(Config.GAME_X + 420, Config.GAME_Y + 5, 200, 50)
            self.news = CyberNewsTicker(0, Config.HEIGHT - 22, Config.WIDTH, 22)
            self.fingerprint = AttackFingerprint(Config.GAME_X + Config.GAME_W - 160, Config.GAME_Y + Config.GAME_H - 110, 155, 105)
        else:
            self.ai_pred = self.hacker_chat = self.heartbeat = self.news = self.fingerprint = None
    
    def _init_nodes(self):
        cx = Config.GAME_X + Config.GAME_W // 2
        cy = Config.GAME_Y + Config.GAME_H // 2
        
        self.server = NetworkNode(cx + 50, cy, NetworkNode.SERVER, "SERVER")
        self.nodes.add(self.server)
        self.fw = NetworkNode(cx - 100, cy, NetworkNode.FIREWALL, "FIREWALL")
        self.nodes.add(self.fw)
        self.router = NetworkNode(Config.GAME_X + 80, cy, NetworkNode.ROUTER, "ROUTER")
        self.nodes.add(self.router)
        
        self.ws = []
        for i, p in enumerate([(cx+180, cy-100), (cx+180, cy+100), (cx+100, cy-180), (cx+100, cy+180)]):
            w = NetworkNode(p[0], p[1], NetworkNode.WORKSTATION, f"WS{i+1}")
            self.nodes.add(w)
            self.ws.append(w)
    
    def _init_ui(self):
        self.hp_bar = HealthBar(Config.GAME_X + 15, Config.GAME_Y + 8, 180, 20, Config.MAX_HP, "HEALTH")
        self.threat_ind = ThreatIndicator(Config.GAME_X + 210, Config.GAME_Y + 3, 120, 40)
        self.def_toggle = DefenseModeToggle(Config.CTRL_X + 5, 85, Config.CTRL_W - 10, 40, self._mode_change)
        
        self.btns = []
        for i, (t, c, f) in enumerate([
            ("BLOCK [Q]", Theme.NEON_RED, self._act_block),
            ("HEAL [E]", Theme.NEON_BLUE, self._act_heal),
            ("CLEAR [C]", Theme.NEON_ORANGE, self._act_clear),
            ("PAUSE", Theme.NEON_YELLOW, self._act_pause)
        ]):
            self.btns.append(CyberButton(Config.CTRL_X + 5, 140 + i * 45, Config.CTRL_W - 10, 38, t, c, f))
        
        self.stats = StatsPanel(Config.SIDE_X, Config.GAME_Y, Config.SIDE_W, 160, "STATS")
        self.log = LogPanel(Config.SIDE_X, Config.GAME_Y + 170, Config.SIDE_W, 160, "LOG")
    
    def _log(self, msg, typ="info"):
        print(f"[{typ.upper()}] {msg}")
        self.log.add_log(msg, typ)
    
    # Callbacks
    def _wave_start(self, n, cfg):
        self.wave_hp = self.hp
        self._log(f"Wave {n}!", "warning")
        if self.voice: self.voice.alert_wave_start(n)
        if self.hacker_chat: self.hacker_chat.trigger_message('boss' if cfg.get('boss_wave') else None)
        if self.news: self.news.add_breaking_news(f"Wave {n} attack detected on network")
        if cfg and cfg.get('boss_wave'):
            self.boss_warn = 150
            if self.boss:
                cx, cy = Config.GAME_X + Config.GAME_W//2, Config.GAME_Y + Config.GAME_H//2
                self.boss.spawn_boss(n, Config.GAME_X + 100, cy, cx, cy)
    
    def _wave_end(self, n):
        self._log(f"Wave {n} done!", "success")
        if self.voice: self.voice.alert_wave_complete(n)
        if self.score: self.score.add_wave_complete_bonus(n, self.hp >= self.wave_hp)
    
    def _combo(self, c):
        self.combo_v, self.combo_t = c, 50
        if c >= 5 and self.voice: self.voice.alert_combo(c)
    
    def _ach(self, a):
        self.popup_ach, self.popup_ach_t = a, 150
        self._log(f"🏆 {a.name}!", "success")
        if self.voice: self.voice.alert_achievement(a.name)
    
    def _mode_change(self, auto):
        self.mode = "AUTO" if auto else "MANUAL"
        self._log(f"Mode: {self.mode}", "success" if auto else "warning")
        if self.voice: self.voice.alert_auto_defense(auto)
    
    def _boss_spawn(self, b):
        self.state = State.BOSS
        self._log(f"BOSS: {b.data['name']}!", "danger")
    
    def _boss_dead(self, b):
        self.state = State.RUN
        self._log("BOSS DEFEATED! +500", "success")
        if self.score: self.score.score += 500
        if self.voice: self.voice.speak("Boss defeated")
    
    def _boss_atk(self, b):
        for _ in range(3):
            self._spawn(f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}", ptype=PacketType.MALICIOUS)
    
    def _pwr(self, p):
        self.popup_pwr, self.popup_pwr_t = p.data['name'], 100
        self._log(f"⚡ {p.data['name']}!", "success")
        if p.power_type == 'heal': self.hp = min(Config.MAX_HP, self.hp + 25)
        elif p.power_type == 'nuke':
            for pkt in list(self.packets):
                if pkt.packet_type == PacketType.MALICIOUS:
                    pkt.block()
                    self.blocked += 1
    
    # Actions
    def _act_block(self):
        cnt = 0
        for p in self.packets:
            if p.packet_type in [PacketType.SUSPICIOUS, PacketType.MALICIOUS] and not p.is_blocked:
                self._block(p)
                cnt += 1
        if cnt:
            self._log(f"Blocked {cnt}", "danger")
            if self.voice: self.voice.alert_ip_blocked()
        if self.boss and self.boss.has_boss():
            self.boss.damage_boss(10)
    
    def _block(self, p):
        p.block()
        self.blocked += 1
        self.particles.emit_block_effect(p.x, p.y)
        self.blocked_ips.add(p.source_ip)
        
        if self.worldmap: self.worldmap.add_attack()
        if self.dna: self.dna.add_attack(p.packet_type.value if hasattr(p.packet_type, 'value') else 'safe')
        if self.fingerprint: self.fingerprint.analyze_attacker(p.source_ip)
        if self.hacker_chat: self.hacker_chat.trigger_message('blocked')
        if self.ai_pred: self.ai_pred.add_attack(random.choice(['DDoS', 'SYN Flood', 'Port Scan', 'Malware']))
        
        if self.score:
            pts = self.score.add_block_score(p.packet_type.value if hasattr(p.packet_type, 'value') else 'safe')
            if self.powerups and self.powerups.has_effect('double_score'):
                self.score.score += pts
            if self.achieve:
                s = self.score.get_stats()
                self.achieve.check_block_achievements(s['total_blocked'])
                self.achieve.check_score_achievements(s['score'])
    
    def _act_heal(self):
        if self.hp < Config.MAX_HP:
            self.hp = min(Config.MAX_HP, self.hp + 25)
            self._log("+25 HP", "success")
    
    def _act_clear(self):
        cnt = len(self.packets)
        for p in list(self.packets):
            self.particles.emit_block_effect(p.x, p.y)
            p.kill()
        self.threat = 0
        self._log(f"Cleared {cnt}", "info")
    
    def _act_pause(self):
        if self.state in [State.RUN, State.BOSS]:
            self.state = State.PAUSE
        elif self.state == State.PAUSE:
            self.state = State.RUN
    
    def _spawn(self, ip="0.0.0.0", ptype=None):
        if len(self.packets) >= Config.MAX_PKT or ip in self.blocked_ips:
            return
        
        if ptype is None:
            if self.waves:
                mc = self.waves.get_malicious_chance()
                w = [1-mc, mc*0.4, mc*0.6]
            else:
                w = [0.6, 0.25, 0.15]
            ptype = random.choices([PacketType.SAFE, PacketType.SUSPICIOUS, PacketType.MALICIOUS], w)[0]
        
        p = PacketSprite(self.router.x, self.router.y, self.server.x, self.server.y, ptype, ip)
        self.packets.add(p)
        self.pkts += 1
        
        if self.mode == "AUTO" and ptype == PacketType.MALICIOUS:
            self._block(p)
        if self.powerups and self.powerups.has_effect('rapid_fire') and ptype == PacketType.MALICIOUS:
            self._block(p)
    
    def _update(self, dt):
        if self.state in [State.PAUSE, State.OVER]:
            return
        
        self.time += dt
        
        if self.waves:
            ws = self.waves.update()
            if ws.get('in_break') and not (self.boss and self.boss.has_boss()):
                if random.random() < 0.01:
                    self._spawn(f"192.168.1.{random.randint(1,254)}")
        
        if self.score: self.score.update()
        if self.worldmap: self.worldmap.update()
        if self.graph: self.graph.add_point(self.threat)
        if self.dna: self.dna.update()
        if self.boss: self.boss.update()
        if self.powerups: self.powerups.update(Config.GAME_X, Config.GAME_Y, Config.GAME_W, Config.GAME_H)
        if self.ai_pred: self.ai_pred.update()
        if self.hacker_chat: self.hacker_chat.update()
        if self.heartbeat: self.heartbeat.update(self.hp)
        if self.news: self.news.update()
        if self.fingerprint: self.fingerprint.update()
        
        # Spawn packets
        rate = self.waves.get_spawn_rate() if self.waves else 0.03
        if random.random() < rate:
            self._spawn(f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}")
        
        self.packets.update()
        self.nodes.update()
        
        # Check arrivals
        for p in list(self.packets):
            if p.reached_target and not p.is_blocked:
                if self.powerups and self.powerups.has_effect('shield'):
                    p.kill()
                    continue
                dmg = p.get_damage()
                if dmg > 0:
                    self.hp -= dmg
                    self.particles.emit_hit_effect(p.x, p.y)
                    if self.hacker_chat: self.hacker_chat.trigger_message('damage')
                    if self.hp < 30 and self.voice and not hasattr(self, '_warned'):
                        self.voice.alert_health_low()
                        self._warned = True
                p.kill()
            elif p.is_blocked and p.alpha <= 0:
                p.kill()
        
        # Threat level
        mal = sum(1 for p in self.packets if p.packet_type == PacketType.MALICIOUS)
        sus = sum(1 for p in self.packets if p.packet_type == PacketType.SUSPICIOUS)
        tgt = min(100, mal * 20 + sus * 8)
        self.threat += (tgt - self.threat) * 0.1
        
        if self.threat >= 70 and self.voice and not hasattr(self, '_crit'):
            self.voice.alert_critical()
            self._crit = True
        
        self.particles.update()
        
        # Popups
        if self.popup_ach_t > 0: self.popup_ach_t -= 1
        if self.popup_pwr_t > 0: self.popup_pwr_t -= 1
        if self.combo_t > 0: self.combo_t -= 1
        if self.boss_warn > 0: self.boss_warn -= 1
        
        # Game over
        if self.hp <= 0:
            self.state = State.OVER
            self._log("GAME OVER!", "danger")
            if self.voice: self.voice.alert_game_over()
            if self.report and self.score and self.achieve:
                self.report.generate(
                    {'game_time': self.time, 'health': self.hp, 'packets_processed': self.pkts},
                    self.score.get_stats(),
                    {'waves_completed': self.waves.waves_completed if self.waves else 0, 'current_wave': self.waves.current_wave if self.waves else 0},
                    self.achieve.get_unlocked()
                )
                self.report.print_report()
    
    def _draw(self):
        self.screen.fill(Config.BG)
        
        # Grid
        for x in range(Config.GAME_X, Config.GAME_X + Config.GAME_W, 40):
            pygame.draw.line(self.screen, Config.GRID, (x, Config.GAME_Y), (x, Config.GAME_Y + Config.GAME_H))
        for y in range(Config.GAME_Y, Config.GAME_Y + Config.GAME_H, 40):
            pygame.draw.line(self.screen, Config.GRID, (Config.GAME_X, y), (Config.GAME_X + Config.GAME_W, y))
        
        # Game border
        bc = (255, 50, 50) if self.state == State.BOSS else Theme.NEON_BLUE
        pygame.draw.rect(self.screen, bc, (Config.GAME_X, Config.GAME_Y, Config.GAME_W, Config.GAME_H), 2)
        
        # Connections
        pygame.draw.line(self.screen, (40, 60, 90), (self.router.x, self.router.y), (self.fw.x, self.fw.y), 2)
        pygame.draw.line(self.screen, (40, 60, 90), (self.fw.x, self.fw.y), (self.server.x, self.server.y), 2)
        for w in self.ws:
            pygame.draw.line(self.screen, (40, 60, 90), (self.server.x, self.server.y), (w.x, w.y), 1)
        
        # Sprites
        for p in self.packets: p.draw_trail(self.screen)
        self.nodes.draw(self.screen)
        self.packets.draw(self.screen)
        if self.powerups: self.powerups.draw(self.screen)
        if self.boss: self.boss.draw(self.screen)
        self.particles.draw(self.screen)
        
        # Fingerprint in game area
        if self.fingerprint: self.fingerprint.draw(self.screen)
        
        # Heartbeat in game area
        if self.heartbeat: self.heartbeat.draw(self.screen)
        
        # HUD
        pygame.draw.rect(self.screen, Theme.PANEL_BG, (0, 0, Config.WIDTH, 55))
        pygame.draw.line(self.screen, Theme.NEON_BLUE, (0, 55), (Config.WIDTH, 55), 2)
        
        t = self.fonts['M'].render("PACKET DEFENDER", True, Theme.NEON_BLUE)
        self.screen.blit(t, (15, 15))
        
        if self.waves:
            wt = self.fonts['S'].render(f"WAVE {self.waves.current_wave}", True, (255, 50, 255) if self.state == State.BOSS else Theme.NEON_PURPLE)
            self.screen.blit(wt, (200, 18))
        
        if self.score:
            st = self.fonts['S'].render(f"SCORE: {self.score.score}", True, Theme.NEON_GREEN)
            self.screen.blit(st, (Config.WIDTH//2 - st.get_width()//2, 10))
            if self.score.combo > 1:
                ct = self.fonts['S'].render(f"x{self.score.combo}", True, Theme.NEON_YELLOW)
                self.screen.blit(ct, (Config.WIDTH//2 - ct.get_width()//2, 30))
        
        mins, secs = int(self.time) // 60, int(self.time) % 60
        tt = self.fonts['S'].render(f"{mins:02d}:{secs:02d}", True, Theme.TEXT_PRIMARY)
        self.screen.blit(tt, (Config.WIDTH - 70, 18))
        
        # Control panel
        pygame.draw.rect(self.screen, Theme.PANEL_BG, (Config.CTRL_X, Config.GAME_Y, Config.CTRL_W, 340), border_radius=5)
        pygame.draw.rect(self.screen, Theme.NEON_PURPLE, (Config.CTRL_X, Config.GAME_Y, Config.CTRL_W, 340), 2, border_radius=5)
        ct = self.fonts['T'].render("CONTROLS", True, Theme.NEON_PURPLE)
        self.screen.blit(ct, (Config.CTRL_X + 8, Config.GAME_Y + 5))
        
        self.def_toggle.draw(self.screen)
        for b in self.btns: b.draw(self.screen)
        
        # Keys hint
        kt = self.fonts['T'].render("Q E C SPACE A R", True, Theme.TEXT_SECONDARY)
        self.screen.blit(kt, (Config.CTRL_X + 8, Config.GAME_Y + 320))
        
        # UI panels
        self.hp_bar.set_value(self.hp)
        self.hp_bar.update()
        self.hp_bar.draw(self.screen)
        
        self.threat_ind.set_level(self.threat)
        self.threat_ind.update()
        self.threat_ind.draw(self.screen)
        
        stats = {"Packets": self.pkts, "Blocked": self.blocked, "Threats": sum(1 for p in self.packets if p.packet_type == PacketType.MALICIOUS), "HP": f"{int(self.hp)}%"}
        if self.score: stats["Score"] = self.score.score
        if self.waves: stats["Wave"] = self.waves.current_wave
        if self.boss and self.boss.has_boss(): stats["Boss"] = self.boss.get_boss().health
        self.stats.set_stats(stats)
        self.stats.draw(self.screen)
        
        self.log.draw(self.screen)
        
        # Advanced panels
        if self.worldmap: self.worldmap.draw(self.screen)
        if self.graph: self.graph.draw(self.screen)
        if self.dna: self.dna.draw(self.screen)
        if self.ai_pred: self.ai_pred.draw(self.screen)
        if self.hacker_chat: self.hacker_chat.draw(self.screen)
        if self.news: self.news.draw(self.screen)
        
        # Popups
        if self.popup_ach and self.popup_ach_t > 0:
            pygame.draw.rect(self.screen, Theme.PANEL_BG, (Config.WIDTH//2 - 120, 70, 240, 45), border_radius=8)
            pygame.draw.rect(self.screen, Theme.NEON_YELLOW, (Config.WIDTH//2 - 120, 70, 240, 45), 2, border_radius=8)
            at = self.fonts['T'].render("🏆 ACHIEVEMENT!", True, Theme.NEON_YELLOW)
            self.screen.blit(at, (Config.WIDTH//2 - at.get_width()//2, 75))
            nt = self.fonts['T'].render(self.popup_ach.name, True, Theme.TEXT_PRIMARY)
            self.screen.blit(nt, (Config.WIDTH//2 - nt.get_width()//2, 93))
        
        if self.popup_pwr and self.popup_pwr_t > 0:
            pt = self.fonts['M'].render(f"⚡ {self.popup_pwr}!", True, (0, 255, 255))
            self.screen.blit(pt, (Config.GAME_X + Config.GAME_W//2 - pt.get_width()//2, Config.GAME_Y + 100))
        
        if self.combo_t > 0 and self.combo_v >= 5:
            ct = self.fonts['L'].render(f"x{self.combo_v}!", True, Theme.NEON_RED if self.combo_v >= 10 else Theme.NEON_YELLOW)
            self.screen.blit(ct, (Config.GAME_X + Config.GAME_W//2 - ct.get_width()//2, Config.GAME_Y + 150))
        
        if self.boss_warn > 0:
            bt = self.fonts['L'].render("⚠️ BOSS ⚠️", True, (255, 50, 50))
            self.screen.blit(bt, (Config.GAME_X + Config.GAME_W//2 - bt.get_width()//2, Config.GAME_Y + 200))
        
        # Overlays
        if self.state == State.PAUSE:
            ov = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 180))
            self.screen.blit(ov, (0, 0))
            pt = self.fonts['L'].render("PAUSED", True, Theme.NEON_YELLOW)
            self.screen.blit(pt, (Config.WIDTH//2 - pt.get_width()//2, Config.HEIGHT//2))
        
        elif self.state == State.OVER:
            ov = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
            ov.fill((50, 0, 0, 200))
            self.screen.blit(ov, (0, 0))
            
            gt = self.fonts['L'].render("GAME OVER", True, Theme.NEON_RED)
            self.screen.blit(gt, (Config.WIDTH//2 - gt.get_width()//2, Config.HEIGHT//2 - 80))
            
            if self.score:
                st = self.fonts['M'].render(f"Score: {self.score.score}", True, Theme.NEON_GREEN)
                self.screen.blit(st, (Config.WIDTH//2 - st.get_width()//2, Config.HEIGHT//2 - 20))
            
            info = f"Blocked: {self.blocked}"
            if self.waves: info += f" | Wave: {self.waves.current_wave}"
            it = self.fonts['S'].render(info, True, Theme.TEXT_PRIMARY)
            self.screen.blit(it, (Config.WIDTH//2 - it.get_width()//2, Config.HEIGHT//2 + 20))
            
            if self.report and self.report.report_data:
                g = self.report.report_data.get('grade', '?')
                grt = self.fonts['L'].render(f"GRADE: {g}", True, Theme.NEON_YELLOW)
                self.screen.blit(grt, (Config.WIDTH//2 - grt.get_width()//2, Config.HEIGHT//2 + 60))
            
            ht = self.fonts['S'].render("R = Restart | ESC = Quit", True, Theme.TEXT_SECONDARY)
            self.screen.blit(ht, (Config.WIDTH//2 - ht.get_width()//2, Config.HEIGHT//2 + 110))
    
    def _events(self):
        mpos = pygame.mouse.get_pos()
        mpressed = pygame.mouse.get_pressed()
        mclick = False
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: self.running = False
                elif e.key == pygame.K_SPACE: self._act_pause()
                elif e.key == pygame.K_r and self.state == State.OVER: self._restart()
                elif e.key == pygame.K_a: self.def_toggle.toggle()
                elif e.key == pygame.K_q: self._act_block()
                elif e.key == pygame.K_e: self._act_heal()
                elif e.key == pygame.K_c: self._act_clear()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mclick = True
                self._click(mpos)
        
        for b in self.btns:
            b.update(mpos, mpressed)
        self.def_toggle.update(mpos, mclick)
    
    def _click(self, pos):
        if self.powerups:
            p = self.powerups.check_collection(pos)
            if p: return
        
        for p in self.packets:
            if p.contains_point(pos) and p.packet_type in [PacketType.SUSPICIOUS, PacketType.MALICIOUS]:
                self._block(p)
                break
        
        if self.boss and self.boss.has_boss():
            b = self.boss.get_boss()
            if math.sqrt((pos[0]-b.x)**2 + (pos[1]-b.y)**2) < 50:
                self.boss.damage_boss(5)
                self.particles.emit_block_effect(b.x, b.y)
    
    def _restart(self):
        self.hp = Config.MAX_HP
        self.pkts = self.blocked = 0
        self.threat = self.time = 0
        self.blocked_ips.clear()
        self.packets.empty()
        self.state = State.RUN
        self.log.clear_logs()
        
        if self.score: self.score.reset()
        if self.waves: self.waves.start_game()
        if self.achieve: self.achieve.reset()
        if self.powerups: self.powerups.clear()
        if hasattr(self, '_warned'): del self._warned
        if hasattr(self, '_crit'): del self._crit
        
        self._log("Restarted", "success")
        if self.voice: self.voice.alert_game_start()
    
    def run(self):
        print("[OK] Game running!")
        while self.running:
            dt = self.clock.tick(Config.FPS) / 1000
            self._events()
            self._update(dt)
            self._draw()
            pygame.display.flip()
        pygame.quit()


def main():
    print()
    print("=" * 60)
    print("  PACKET DEFENDER - ULTIMATE EDITION")
    print("  All Features: Voice | Waves | Boss | AI | Hacker Chat")
    print("=" * 60)
    print()
    Game().run()


if __name__ == "__main__":
    main()
