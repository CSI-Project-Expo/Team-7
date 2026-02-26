"""
===========================================================
PACKET DEFENDER - Firewall Engine
===========================================================
- Real iptables integration (Kali Linux)
- 17 toggleable rules across 4 tiers
- Attack database with full explanations
- Smart suggestion engine
- All rules OFF by default
===========================================================
"""

import subprocess
import logging
import os
import time
import random
from datetime import datetime

# Import Config for initial blacklists
try:
    from config import BLACKLISTED_IPS
except ImportError:
    BLACKLISTED_IPS = []

# Import Logger (#28)
from logger import log_event, EventType


logging.basicConfig(
    filename='firewall_log.txt',
    level=logging.INFO,
    format='%(levelname)s | %(message)s'
)


# ─────────────────────────────────────────────
#  ATTACK DATABASE
# ─────────────────────────────────────────────

class AttackDatabase:
    ATTACKS = {
        "SYN_FLOOD": {
            "name": "SYN Flood",
            "icon": "!SYN",
            "severity": "CRITICAL",
            "damage": 8,
            "color": (255, 60, 60),
            "protocol": "TCP",
            "explanation": (
                "Attacker sends thousands of TCP SYN requests without "
                "completing the 3-way handshake. The server allocates "
                "memory for each half-open connection, eventually "
                "exhausting all available slots. Legitimate users "
                "cannot establish new connections."
            ),
            "countered_by": ["syn_cookies", "conn_throttle", "deep_scan"],
            "terminal_log": [
                "TCP SYN received from {ip} -> port 80",
                "SYN-ACK sent, awaiting ACK...",
                "TIMEOUT: No ACK received (half-open)",
                "WARNING: {count} half-open connections active",
                "ALERT: Connection table at {pct}% capacity",
            ],
        },
        "PORT_SCAN": {
            "name": "Port Scan",
            "icon": "SCAN",
            "severity": "MEDIUM",
            "damage": 3,
            "color": (255, 165, 0),
            "protocol": "TCP/UDP",
            "explanation": (
                "Attacker systematically probes TCP and UDP ports "
                "to discover running services. Each open port is a "
                "potential entry point. Tools like Nmap can map your "
                "entire network topology in seconds, revealing OS "
                "versions, service banners, and vulnerabilities."
            ),
            "countered_by": ["close_ssh", "close_ftp", "stealth_ports"],
            "terminal_log": [
                "Connection attempt from {ip} -> port {port}",
                "Port {port}: {status}",
                "Sequential scan detected: ports 1-1024",
                "Service fingerprint: {service}",
                "ALERT: Network reconnaissance in progress",
            ],
        },
        "DNS_SPOOF": {
            "name": "DNS Spoofing",
            "icon": "DNS!",
            "severity": "HIGH",
            "damage": 7,
            "color": (200, 0, 200),
            "protocol": "UDP (DNS)",
            "explanation": (
                "Attacker injects forged DNS responses into the "
                "cache so that victims connect to malicious servers "
                "instead of legitimate ones. Users believe they are "
                "on a trusted website but all data — passwords, "
                "credit cards — goes directly to the attacker."
            ),
            "countered_by": ["dns_verify", "deep_scan", "protocol_check"],
            "terminal_log": [
                "DNS query: {domain} -> {ip}",
                "Response received from unexpected source",
                "TTL mismatch: expected 3600, got 60",
                "ALERT: DNS cache poisoning attempt detected",
                "Redirecting traffic to {fake_ip}",
            ],
        },
        "DDOS": {
            "name": "DDoS Attack",
            "icon": "DDoS",
            "severity": "CRITICAL",
            "damage": 12,
            "color": (255, 0, 0),
            "protocol": "TCP/UDP/ICMP",
            "explanation": (
                "Distributed Denial-of-Service floods the target "
                "from hundreds or thousands of compromised machines "
                "simultaneously. Network bandwidth, CPU, and memory "
                "are overwhelmed. Even powerful servers buckle under "
                "volumetric attacks exceeding 100 Gbps."
            ),
            "countered_by": ["rate_limit", "conn_throttle", "geo_filter", "udp_guard"],
            "terminal_log": [
                "Incoming: {rate} requests/sec from {ip}",
                "Bandwidth: {bw} Mbps (threshold: 100 Mbps)",
                "CPU utilization: {cpu}%",
                "Memory: {ram}% used",
                "CRITICAL: Service degradation detected",
            ],
        },
        "BRUTE_FORCE": {
            "name": "Brute Force",
            "icon": "BF!!",
            "severity": "HIGH",
            "damage": 6,
            "color": (255, 100, 100),
            "protocol": "TCP (SSH/FTP)",
            "explanation": (
                "Attacker uses automated tools to try thousands of "
                "username and password combinations per minute against "
                "SSH, FTP, or web login forms. Weak passwords like "
                "'admin123' fall in seconds. Strong 16-character "
                "passwords would take centuries to crack."
            ),
            "countered_by": ["close_ssh", "login_guard", "auto_ban", "remove_defaults", "hardened_auth"],
            "terminal_log": [
                "SSH login attempt: {user}@{ip}",
                "Authentication FAILED for {user}",
                "Attempt {count}/10000 from {ip}",
                "Password tried: {pwd}",
                "ALERT: Brute force attack on SSH detected",
            ],
        },
        "MALWARE": {
            "name": "Malware Payload",
            "icon": "MAL!",
            "severity": "CRITICAL",
            "damage": 10,
            "color": (180, 0, 0),
            "protocol": "TCP/UDP/HTTP",
            "explanation": (
                "Packet carries executable malware — ransomware, "
                "trojans, rootkits, or worms. Once inside the network, "
                "it can encrypt all files for ransom, steal sensitive "
                "data, create backdoors for persistent access, or "
                "spread to other machines automatically."
            ),
            "countered_by": ["deep_scan", "payload_filter", "protocol_check", "integrity_check", "tls_encryption"],
            "terminal_log": [
                "Payload received: {size} bytes from {ip}",
                "Content-Type: application/x-executable",
                "Signature match: {malware_name}",
                "Hash: {hash}",
                "CRITICAL: Malicious payload detected!",
            ],
        },
        "PING_FLOOD": {
            "name": "Ping Flood",
            "icon": "PING",
            "severity": "MEDIUM",
            "damage": 4,
            "color": (255, 200, 0),
            "protocol": "ICMP",
            "explanation": (
                "Massive ICMP echo-request packets consume bandwidth "
                "and CPU processing power. Simple but effective — even "
                "basic tools like 'ping -f' can significantly slow "
                "down unprotected servers. Often used as a distraction "
                "while other attacks proceed quietly."
            ),
            "countered_by": ["icmp_block", "rate_limit", "conn_throttle", "enhanced_logging"],
            "terminal_log": [
                "ICMP echo-request from {ip} (size: {size})",
                "Ping rate: {rate}/sec (normal: 1/sec)",
                "ICMP flood detected from {ip}",
                "Bandwidth consumed: {bw} Mbps",
                "ALERT: ICMP flood in progress",
            ],
        },
        "SQL_INJECTION": {
            "name": "SQL Injection",
            "icon": "SQLi",
            "severity": "CRITICAL",
            "damage": 9,
            "color": (150, 0, 150),
            "protocol": "TCP (HTTP)",
            "explanation": (
                "Malicious SQL commands injected through web forms "
                "or URL parameters bypass authentication and directly "
                "access the database. A single unvalidated input field "
                "can let attackers read all user data, modify records, "
                "delete tables, or even execute system commands."
            ),
            "countered_by": ["payload_filter", "deep_scan", "input_guard", "enhanced_logging", "tls_encryption"],
            "terminal_log": [
                "POST /login HTTP/1.1 from {ip}",
                "Input: username=' OR 1=1 --",
                "SQL query modified: SELECT * FROM users",
                "WARNING: SQL injection pattern detected",
                "ALERT: Database breach attempt!",
            ],
        },
        "UNKNOWN": {
            "name": "Unknown Threat",
            "icon": "???",
            "severity": "MEDIUM",
            "damage": 5,
            "color": (200, 100, 0),
            "protocol": "UNKNOWN",
            "explanation": "Unidentified network anomaly or suspicious activity detected by sensors.",
            "countered_by": ["deep_scan", "protocol_check"],
            "terminal_log": [
                "ANOMALY: Unexpected traffic pattern from {ip}",
                "WARNING: Unclassified signature match",
                "ALERT: Heuristic analysis flagged suspicious packet",
            ],
        },
    }

    @classmethod
    def get(cls, attack_id):
        return cls.ATTACKS.get(attack_id)

    @classmethod
    def all_ids(cls):
        return list(cls.ATTACKS.keys())

    @classmethod
    def random_attack(cls, mal_chance=0.4):
        if random.random() > mal_chance:
            return "SAFE"
        return random.choice(list(cls.ATTACKS.keys()))

    @classmethod
    def get_damage(cls, aid):
        i = cls.ATTACKS.get(aid)
        return i["damage"] if i else 0

    @classmethod
    def get_severity(cls, aid):
        i = cls.ATTACKS.get(aid)
        return i["severity"] if i else "LOW"

    @classmethod
    def get_color(cls, aid):
        i = cls.ATTACKS.get(aid)
        return i["color"] if i else (150, 150, 150)

    @classmethod
    def get_explanation(cls, aid):
        i = cls.ATTACKS.get(aid)
        return i["explanation"] if i else ""

    @classmethod
    def get_counters(cls, aid):
        i = cls.ATTACKS.get(aid)
        return i["countered_by"] if i else []

    @classmethod
    def get_terminal_log(cls, aid, ip="0.0.0.0"):
        i = cls.ATTACKS.get(aid)
        if not i:
            return ""
        templates = i.get("terminal_log", [])
        if not templates:
            return ""
        template = random.choice(templates)
        replacements = {
            "{ip}": ip,
            "{port}": str(random.choice([22, 80, 443, 3306, 21, 8080, 23, 53])),
            "{status}": random.choice(["OPEN", "FILTERED", "CLOSED"]),
            "{service}": random.choice(["OpenSSH 7.9", "Apache 2.4", "MySQL 5.7", "vsftpd 3.0"]),
            "{domain}": random.choice(["google.com", "bank.com", "login.secure.net"]),
            "{fake_ip}": f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}",
            "{rate}": str(random.randint(500, 5000)),
            "{bw}": str(random.randint(50, 500)),
            "{cpu}": str(random.randint(70, 99)),
            "{ram}": str(random.randint(75, 99)),
            "{user}": random.choice(["root", "admin", "user", "oracle", "postgres"]),
            "{pwd}": random.choice(["admin123", "password", "12345", "qwerty", "letmein"]),
            "{count}": str(random.randint(100, 9999)),
            "{pct}": str(random.randint(70, 99)),
            "{size}": str(random.randint(64, 65535)),
            "{malware_name}": random.choice(["Trojan.GenericKD", "Ransomware.WannaCry", "Rootkit.Hidden", "Worm.Conficker"]),
            "{hash}": f"{random.randint(0,0xFFFFFFFF):08x}...{random.randint(0,0xFFFF):04x}",
        }
        for k, v in replacements.items():
            template = template.replace(k, v)
        return template


# ─────────────────────────────────────────────
#  DEFENSE RULE
# ─────────────────────────────────────────────

class DefenseRule:
    def __init__(self, rule_id, name, tier, description, effectiveness):
        self.rule_id = rule_id
        self.name = name
        self.tier = tier
        self.description = description
        self.effectiveness = effectiveness
        self.enabled = False
        self.blocks_count = 0

    def toggle(self):
        self.enabled = not self.enabled
        return self.enabled


# ─────────────────────────────────────────────
#  IPTABLES CONTROLLER
# ─────────────────────────────────────────────

class IPTablesController:
    def __init__(self):
        self.blocked_ips = set()
        self.is_root = self._check_root()
        if self.is_root:
            print("[IPTABLES] Running as root — real blocking enabled")
        else:
            print("[IPTABLES] Not root — simulation mode")

    def _check_root(self):
        try:
            return os.geteuid() == 0
        except:
            return False

    def _run(self, args):
        try:
            r = subprocess.run(['iptables'] + args, capture_output=True, text=True, timeout=10)
            return r.returncode == 0
        except:
            return False

    def block_ip(self, ip):
        if not self._valid(ip) or ip in self.blocked_ips:
            return False
        sin = self._run(['-A', 'INPUT', '-s', ip, '-j', 'DROP'])
        self._run(['-A', 'OUTPUT', '-d', ip, '-j', 'DROP'])
        if sin:
            self.blocked_ips.add(ip)
            log_event(EventType.BLOCK.value, f"IPTABLES BLOCKED: {ip}")
            return True
        return False

    def unblock_ip(self, ip):
        if ip not in self.blocked_ips:
            return True
        self._run(['-D', 'INPUT', '-s', ip, '-j', 'DROP'])
        self._run(['-D', 'OUTPUT', '-d', ip, '-j', 'DROP'])
        self.blocked_ips.discard(ip)
        log_event(EventType.UNBLOCK.value, f"IPTABLES UNBLOCKED: {ip}")
        return True

    def clear_all(self):
        for ip in list(self.blocked_ips):
            self.unblock_ip(ip)

    def _valid(self, ip):
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except:
            return False

    def get_status(self):
        return {
            'is_root': self.is_root,
            'total_blocked': len(self.blocked_ips),
            'blocked_ips': list(self.blocked_ips),
        }


# ─────────────────────────────────────────────
#  SMART SUGGESTION ENGINE
# ─────────────────────────────────────────────

class SuggestionEngine:
    """
    Analyzes current attacks and disabled rules.
    Gives real-time tips to the player.
    """

    def __init__(self, defense_engine):
        self.defense = defense_engine
        self.current_tip = ""
        self.tip_timer = 0
        self.tip_cooldown = 0
        self.last_attacks = []

    def analyze(self, active_attack_ids):
        """Call every frame with list of current attack IDs on screen"""
        if self.tip_cooldown > 0:
            self.tip_cooldown -= 1
            return

        if not active_attack_ids:
            self.current_tip = ""
            return

        # Find attacks that have disabled counters
        for aid in active_attack_ids:
            info = AttackDatabase.get(aid)
            if not info:
                continue
            counters = info.get("countered_by", [])
            disabled = []
            for cid in counters:
                rule = self.defense.get_rule(cid)
                if rule and not rule.enabled:
                    disabled.append(rule.name)

            if disabled:
                self.current_tip = f"TIP: Enable '{disabled[0]}' to counter {info['name']}"
                self.tip_timer = 180
                self.tip_cooldown = 300  # Don't spam
                return

        self.current_tip = ""

    def get_tip(self):
        if self.tip_timer > 0:
            self.tip_timer -= 1
            return self.current_tip
        return ""


# ─────────────────────────────────────────────
#  DEFENSE ENGINE
# ─────────────────────────────────────────────

class DefenseEngine:
    TIER_NAMES = {
        1: "Port Security",
        2: "Traffic Control",
        3: "Packet Inspection",
        4: "Advanced Defense",
        5: "Service Hardening",
        6: "Access Control",
        7: "Monitoring & Detection",
        8: "Backup & Recovery"
    }

    RULE_DEFS = {
        # ... existing rules ...
        "close_ssh": {
            "name": "Close SSH (Port 22)",
            "tier": 1,
            "description": "Shuts down the SSH port (22) to prevent all remote login attempts.",
            "effectiveness": 1.0,
        },
        "close_ftp": {
            "name": "Close FTP (Port 21)",
            "tier": 1,
            "description": "Blocks the FTP file transfer port entirely.",
            "effectiveness": 1.0,
        },
        "stealth_ports": {
            "name": "Stealth Mode",
            "tier": 1,
            "description": "Silently drop packets instead of responding with 'connection refused'.",
            "effectiveness": 0.90,
        },
        "close_telnet": {
            "name": "Close Telnet (Port 23)",
            "tier": 1,
            "description": "Disables the Telnet protocol.",
            "effectiveness": 1.0,
        },
        "rate_limit": {
            "name": "Rate Limiter",
            "tier": 2,
            "description": "Caps incoming connection requests per second.",
            "effectiveness": 0.85,
        },
        "conn_throttle": {
            "name": "Connection Throttle",
            "tier": 2,
            "description": "Limits simultaneous open connections from each source IP.",
            "effectiveness": 0.80,
        },
        "syn_cookies": {
            "name": "SYN Cookies",
            "tier": 2,
            "description": "Defeats SYN flood attacks with zero performance cost.",
            "effectiveness": 1.0,
        },
        "udp_guard": {
            "name": "UDP Flood Guard",
            "tier": 2,
            "description": "Monitors and filters excessive UDP traffic.",
            "effectiveness": 0.85,
        },
        "deep_scan": {
            "name": "Deep Packet Inspection",
            "tier": 3,
            "description": "Examines full payload against malware signatures.",
            "effectiveness": 0.95,
        },
        "payload_filter": {
            "name": "Payload Filter",
            "tier": 3,
            "description": "Scans request bodies for dangerous content patterns.",
            "effectiveness": 0.90,
        },
        "protocol_check": {
            "name": "Protocol Validator",
            "tier": 3,
            "description": "Verifies that packets follow protocol specifications.",
            "effectiveness": 0.80,
        },
        "input_guard": {
            "name": "Input Sanitizer",
            "tier": 3,
            "description": "Inspects web form submissions for injection patterns.",
            "effectiveness": 0.95,
        },
        "icmp_block": {
            "name": "ICMP Filter",
            "tier": 4,
            "description": "Blocks or rate-limits ICMP echo requests (ping).",
            "effectiveness": 1.0,
        },
        "dns_verify": {
            "name": "DNS Verification",
            "tier": 4,
            "description": "Cross-checks DNS responses against trusted servers.",
            "effectiveness": 1.0,
        },
        "geo_filter": {
            "name": "Geo-IP Filter",
            "tier": 4,
            "description": "Blocks traffic from high-attack geographic regions.",
            "effectiveness": 0.80,
        },
        "auto_ban": {
            "name": "Auto Blacklist",
            "tier": 4,
            "description": "Automatically adds repeat offenders to blacklist.",
            "effectiveness": 1.0,
        },
        "login_guard": {
            "name": "Login Limiter",
            "tier": 4,
            "description": "Locks out source IPs with too many failed logins.",
            "effectiveness": 1.0,
        },
        # SERVER CONFIGURATION RULES
        "disable_ftp_srv": {
            "name": "Disable FTP Service",
            "tier": 5,
            "description": "Stops the FTP daemon on the server. Prevents any file transfers even if the port is open.",
            "effectiveness": 1.0,
        },
        "disable_telnet_srv": {
            "name": "Disable Telnet Srv",
            "tier": 5,
            "description": "Shuts down the Telnet service daemon. Essential for service hardening.",
            "effectiveness": 1.0,
        },
        "tls_encryption": {
            "name": "Enable TLS Encryption",
            "tier": 5,
            "description": "Enforces TLS for all communications, preventing eavesdropping and MITM attacks.",
            "effectiveness": 0.9,
        },
        "remove_defaults": {
            "name": "Remove Default Accounts",
            "tier": 6,
            "description": "Deletes factory-default credentials (e.g., admin/admin) that are targeted by bots.",
            "effectiveness": 1.0,
        },
        "hardened_auth": {
            "name": "Hardened Auth",
            "tier": 6,
            "description": "Implements multi-factor authentication and strict password complexity policies.",
            "effectiveness": 0.95,
        },
        "integrity_check": {
            "name": "File Integrity Mon",
            "tier": 7,
            "description": "Monitors system files for unauthorized changes. Detects rootkits and backdoors.",
            "effectiveness": 0.85,
        },
        "enhanced_logging": {
            "name": "Enhanced Logging",
            "tier": 7,
            "description": "Detailed logging of all system events for forensic analysis and threat detection.",
            "effectiveness": 0.7,
        },
        "disable_root_login": {
            "name": "Disable Root Login",
            "tier": 6,
            "description": "Prevents the 'root' user from logging in directly. Forces use of non-privileged accounts.",
            "effectiveness": 0.95,
        },
        "enable_2fa": {
            "name": "Enable 2FA",
            "tier": 6,
            "description": "Requires a second form of verification for all logins, neutralizing most stolen credentials.",
            "effectiveness": 0.98,
        },
        "ssh_key_only": {
            "name": "SSH Key Auth Only",
            "tier": 6,
            "description": "Disables password-based SSH logins. Only users with registered cryptographic keys can enter.",
            "effectiveness": 1.0,
        },
        "ip_whitelisting": {
            "name": "IP Whitelisting",
            "tier": 6,
            "description": "Only allows connections from a pre-approved list of trusted IP addresses.",
            "effectiveness": 0.9,
        },
        "enable_ids": {
            "name": "Enable IDS",
            "tier": 7,
            "description": "Activates Intrusion Detection System to monitor network traffic for suspicious patterns.",
            "effectiveness": 0.85,
        },
        "log_all_access": {
            "name": "Log All Access",
            "tier": 7,
            "description": "Maintains a comprehensive audit trail of every connection attempt to the server.",
            "effectiveness": 0.6,
        },
        "failed_login_alerts": {
            "name": "Failed Login Alerts",
            "tier": 7,
            "description": "Triggers immediate security notifications after multiple unsuccessful login attempts.",
            "effectiveness": 0.8,
        },
        "auto_backups": {
            "name": "Automatic Backups",
            "tier": 8,
            "description": "Regularly archives system state to secure storage to ensure rapid recovery from data loss.",
            "effectiveness": 1.0,
        },
        "db_encryption": {
            "name": "DB Encryption",
            "tier": 8,
            "description": "Protects sensitive data at rest using strong encryption standards.",
            "effectiveness": 0.9,
        },
        "disaster_recovery": {
            "name": "Disaster Recovery",
            "tier": 8,
            "description": "Implements a structured plan to restore services after a catastrophic system failure.",
            "effectiveness": 0.95,
        },
        "audit_trail": {
            "name": "Audit Trail Logging",
            "tier": 8,
            "description": "Ensures non-repudiation by logging all administrative actions performed on the system.",
            "effectiveness": 0.8,
        }
    }


    def __init__(self):
        self.rules = {}
        for rid, data in self.RULE_DEFS.items():
            self.rules[rid] = DefenseRule(
                rule_id=rid, name=data["name"], tier=data["tier"],
                description=data["description"], effectiveness=data["effectiveness"]
            )

        self.iptables = IPTablesController()
        self.suggestions = SuggestionEngine(self)
        self.total_blocked = 0
        self.total_passed = 0
        self.blocked_ips = set(BLACKLISTED_IPS)
        self.log = []
        self._log("Firewall engine online — all rules OFF")
        logging.info("DefenseEngine initialized")

    def can_block(self, attack_id):
        """Returns True only if ALL active rules required for this attack_id are enabled"""
        if not attack_id or attack_id == "SAFE":
            return False
            
        info = AttackDatabase.get(attack_id)
        if not info:
            return False
            
        counters = info.get("countered_by", [])
        if not counters:
            return False

        for cid in counters:
            rule = self.rules.get(cid)
            if not rule or not rule.enabled:
                return False
        return True

    def toggle_rule(self, rid):
        r = self.rules.get(rid)
        if not r: return None
        state = r.toggle()
        self._log(f"{r.name} [{'ENABLED' if state else 'DISABLED'}]")
        logging.info(f"Rule {rid}: {'ENABLED' if state else 'DISABLED'}")
        return state

    def enable_all(self):
        for r in self.rules.values(): r.enabled = True
        self._log("ALL RULES ENABLED")

    def disable_all(self):
        for r in self.rules.values(): r.enabled = False
        self._log("ALL RULES DISABLED")

    def inspect_packet(self, attack_id, source_ip=None):
        # Only check blacklist if 'auto_ban' rule is enabled
        auto_ban_rule = self.rules.get("auto_ban")
        if auto_ban_rule and auto_ban_rule.enabled:
            if source_ip and source_ip in self.blocked_ips:
                self.total_blocked += 1
                return True, "Blacklist", AttackDatabase.get(attack_id) or {
                    "name": "Unknown Threat", "color": (255, 50, 50), "damage": 5, "icon": "???"
                }, 1.0

        if not attack_id or attack_id == "SAFE":
            self.total_passed += 1
            return False, None, None, 0.0

        info = AttackDatabase.get(attack_id)
        if not info:
            self.total_passed += 1
            return False, None, None, 0.0

        counters = info.get("countered_by", [])
        
        # REQUIRE ALL RULES: Check if ALL required rules are enabled
        disabled_rules = []
        for cid in counters:
            rule = self.rules.get(cid)
            if not rule or not rule.enabled:
                disabled_rules.append(rule.name if rule else cid)
        
        if disabled_rules:
            self.total_passed += 1
            # We return False (not blocked) but pass the list of missing rules in rule_name slot
            # Or we can change the return signature, but let's stick to 4 values for now
            # and use a special string if needed or just return None and let main.py handle it.
            # Actually, let's return the list as a string in rule_name if blocked is False.
            return False, ", ".join(disabled_rules), info, 0.0

        # If we reach here, all required rules are enabled
        combined = 0.0
        best_rule = None
        best_eff = 0.0

        for cid in counters:
            rule = self.rules.get(cid)
            if rule and rule.enabled:
                eff = rule.effectiveness
                combined = 1.0 - (1.0 - combined) * (1.0 - eff)
                if eff > best_eff:
                    best_eff = eff
                    best_rule = rule

        if combined > 0:
            if best_rule: best_rule.blocks_count += 1
            self.total_blocked += 1
            
            # Only add to blacklist/iptables if 'auto_ban' is enabled
            if auto_ban_rule and auto_ban_rule.enabled:
                if source_ip and self._is_external(source_ip):
                    self.iptables.block_ip(source_ip)
                self.blocked_ips.add(source_ip or "unknown")
                
            self._log(f"BLOCKED {info['name']} [{source_ip or '?'}]")
            return True, best_rule.name if best_rule else "Firewall", info, combined
        else:
            self.total_passed += 1
            return False, None, info, combined

    def _is_external(self, ip):
        if not ip: return False
        if ip.startswith(("192.168.", "10.", "127.")): return False
        parts = ip.split('.')
        if len(parts) != 4: return False
        try:
            return all(0 <= int(p) <= 255 for p in parts)
        except: return False

    def get_rule(self, rid):
        return self.rules.get(rid)

    def get_rules_by_tier(self, tier):
        return [r for r in self.rules.values() if r.tier == tier]

    def get_all_rules(self):
        return list(self.rules.values())

    def active_count(self):
        return sum(1 for r in self.rules.values() if r.enabled)

    def total_rules(self):
        return len(self.rules)

    def get_tier_name(self, tier):
        return self.TIER_NAMES.get(tier, f"Tier {tier}")

    def get_rule_status(self):
        out = {}
        for rid, r in self.rules.items():
            out[rid] = {
                "name": r.name, "tier": r.tier, "enabled": r.enabled,
                "description": r.description, "effectiveness": r.effectiveness,
                "count": r.blocks_count,
            }
        return out

    def get_stats(self):
        return {
            "total_blocked": self.total_blocked,
            "total_passed": self.total_passed,
            "active_rules": self.active_count(),
            "total_rules": self.total_rules(),
            "blocked_ips": len(self.blocked_ips),
            "iptables_blocked": len(self.iptables.blocked_ips),
        }

    def get_defense_score(self):
        if self.total_rules() == 0: return 0
        return int((self.active_count() / self.total_rules()) * 100)

    def get_suggestion(self, attack_ids):
        self.suggestions.analyze(attack_ids)
        return self.suggestions.get_tip()

    def _log(self, msg):
        self.log.append(f"[FW] {msg}")
        if len(self.log) > 200:
            self.log = self.log[-150:]

    def recent_logs(self, n=20):
        return self.log[-n:]

    def reset(self):
        for r in self.rules.values():
            r.enabled = False
            r.blocks_count = 0
        self.total_blocked = 0
        self.total_passed = 0
        self.blocked_ips.clear()
        self.iptables.clear_all()
        self.log.clear()
        self._log("Firewall RESET — all rules OFF")

    def cleanup(self):
        self.iptables.clear_all()
        logging.info("DefenseEngine cleanup")
