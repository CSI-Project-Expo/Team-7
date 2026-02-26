"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                         CYBER DEFENSE SIMULATION GAME                        ║
║                            Configuration Module                              ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   Description : Central configuration file containing all constants,        ║
║                 IP blacklists, whitelists, color codes, and settings        ║
║                 used across the entire simulation.                           ║
║                                                                              ║
║   Author      : [Your Name]                                                  ║
║   Team        : [Your Team Name]                                             ║
║   Version     : 1.0.0                                                        ║
║   Last Update : [Date]                                                       ║
║                                                                              ║
║   Usage       : Import this module in any file that needs configuration     ║
║                 Example: from config import BLACKLISTED_IPS, COLORS          ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════
#                              OPERATION MODES
# ═══════════════════════════════════════════════════════════════════════════════

# Set to True for demo/presentation (generates fake packets)
# Set to False for real network capture (requires admin/root privileges)
SIMULATION_MODE = True

# Debug mode - enables verbose console output
DEBUG_MODE = True

# ═══════════════════════════════════════════════════════════════════════════════
#                           NETWORK INTERFACE SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Network interface for packet capture
# Common values:
#   Windows : "Ethernet", "Wi-Fi", "eth0"
#   Linux   : "eth0", "wlan0", "enp0s3"
#   macOS   : "en0", "en1"
NETWORK_INTERFACE = "eth0"

# Backup interfaces to try if primary fails
BACKUP_INTERFACES = ["wlan0", "Wi-Fi", "Ethernet", "en0", "enp0s3"]

# ═══════════════════════════════════════════════════════════════════════════════
#                              QUEUE SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Maximum packets in queue before dropping old ones
MAX_QUEUE_SIZE = 500

# Timeout for queue operations (seconds)
QUEUE_TIMEOUT = 0.05

# ═══════════════════════════════════════════════════════════════════════════════
#                           PACKET RATE SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Packets generated per second during normal simulation
NORMAL_PACKET_RATE = 2

# Packets generated per second during attack simulation
ATTACK_PACKET_RATE = 50

# Maximum packets per second (safety limit)
MAX_PACKET_RATE = 200

# ═══════════════════════════════════════════════════════════════════════════════
#                                IP LISTS
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# WHITELISTED IPs - Trusted sources (will appear as BLUE/SAFE)
# These are known good IPs that should never be blocked
# ─────────────────────────────────────────────────────────────────────────────
WHITELISTED_IPS = [
    # Local network
    "127.0.0.1",          # Localhost
    "192.168.1.1",        # Default gateway
    "192.168.1.10",       # Trusted workstation
    "192.168.1.20",       # Trusted workstation
    "192.168.1.100",      # Internal server
    
    # Private network ranges (common)
    "10.0.0.1",           # Gateway
    "10.0.0.5",           # DNS server
    "172.16.0.1",         # Gateway
    
    # Known good external (examples)
    "8.8.8.8",            # Google DNS
    "8.8.4.4",            # Google DNS
    "1.1.1.1",            # Cloudflare DNS
]

# ─────────────────────────────────────────────────────────────────────────────
# BLACKLISTED IPs - Known malicious sources (will appear as RED/SKULL)
# These IPs are confirmed threats and should be blocked immediately
# ─────────────────────────────────────────────────────────────────────────────
BLACKLISTED_IPS = [
    # Known malicious IPs (examples - fictional for simulation)
    "103.75.201.2",
    "185.156.73.54",
    "45.155.205.233",
    "194.26.192.64",
    "89.248.165.52",
    "45.146.164.110",
    "185.220.101.1",
    "23.129.64.100",
    "91.240.118.172",
    "185.100.87.41",
]

# ─────────────────────────────────────────────────────────────────────────────
# SUSPICIOUS IPs - Potentially dangerous (will appear as ORANGE/YELLOW)
# These need monitoring but aren't confirmed threats
# ─────────────────────────────────────────────────────────────────────────────
SUSPICIOUS_IPS = [
    "45.33.32.156",       # Unknown scanner
    "199.87.154.255",     # Suspicious activity
    "91.189.91.157",      # Unusual traffic
    "104.131.0.69",       # Potential probe
    "178.62.0.100",       # Unverified source
]

# ─────────────────────────────────────────────────────────────────────────────
# SERVER IPs - Our protected assets (targets of attacks)
# ─────────────────────────────────────────────────────────────────────────────
SERVER_IPS = [
    "192.168.1.100",      # Web Server
    "192.168.1.101",      # Database Server
    "192.168.1.102",      # File Server
    "192.168.1.103",      # Mail Server
    "192.168.1.104",      # Application Server
]

# ═══════════════════════════════════════════════════════════════════════════════
#                              COLOR CODES
# ═══════════════════════════════════════════════════════════════════════════════

# RGB color tuples for Pygame visualization
COLORS = {
    # ─── Threat Level Colors ───────────────────────────────────────────────
    "SAFE": (0, 191, 255),           # Deep Sky Blue - trusted traffic
    "UNKNOWN": (255, 255, 0),        # Yellow - unclassified
    "SUSPICIOUS": (255, 165, 0),     # Orange - needs attention
    "HOSTILE": (255, 50, 50),        # Red - dangerous
    "CRITICAL": (148, 0, 211),       # Purple - severe threat
    "BLOCKED": (128, 128, 128),      # Gray - blocked packets
    
    # ─── Protocol Colors ───────────────────────────────────────────────────
    "TCP": (0, 150, 255),            # Blue
    "UDP": (255, 200, 0),            # Gold
    "ICMP": (0, 255, 150),           # Cyan-Green
    "HTTP": (100, 149, 237),         # Cornflower Blue
    "HTTPS": (50, 205, 50),          # Lime Green
    "DNS": (255, 105, 180),          # Hot Pink
    "SSH": (255, 140, 0),            # Dark Orange
    "FTP": (220, 20, 60),            # Crimson
    
    # ─── UI Colors ─────────────────────────────────────────────────────────
    "BACKGROUND": (15, 20, 35),      # Dark blue-gray
    "PANEL": (25, 35, 55),           # Slightly lighter
    "TEXT": (255, 255, 255),         # White
    "TEXT_DIM": (150, 150, 150),     # Gray text
    "HEALTH_GOOD": (0, 255, 100),    # Green
    "HEALTH_MED": (255, 255, 0),     # Yellow
    "HEALTH_LOW": (255, 50, 50),     # Red
    "BORDER": (100, 100, 150),       # Light border
}

# ═══════════════════════════════════════════════════════════════════════════════
#                             THREAT LEVELS
# ═══════════════════════════════════════════════════════════════════════════════

# Threat level definitions with associated properties
THREAT_LEVELS = {
    "SAFE": {
        "level": 0,
        "color": COLORS["SAFE"],
        "sprite": "blue",
        "damage": 0,
        "label": "Safe Traffic",
        "description": "Trusted source, no action needed",
        "priority": 1,
    },
    "UNKNOWN": {
        "level": 1,
        "color": COLORS["UNKNOWN"],
        "sprite": "yellow",
        "damage": 1,
        "label": "Unknown Source",
        "description": "Unverified source, monitoring",
        "priority": 2,
    },
    "SUSPICIOUS": {
        "level": 2,
        "color": COLORS["SUSPICIOUS"],
        "sprite": "orange",
        "damage": 3,
        "label": "Suspicious Activity",
        "description": "Potentially dangerous, investigate",
        "priority": 3,
    },
    "HOSTILE": {
        "level": 3,
        "color": COLORS["HOSTILE"],
        "sprite": "red",
        "damage": 5,
        "label": "Hostile Traffic",
        "description": "Confirmed threat, block recommended",
        "priority": 4,
    },
    "CRITICAL": {
        "level": 4,
        "color": COLORS["CRITICAL"],
        "sprite": "skull",
        "damage": 10,
        "label": "Critical Threat",
        "description": "Severe attack, immediate action required",
        "priority": 5,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
#                              PROTOCOLS
# ═══════════════════════════════════════════════════════════════════════════════

# Protocol definitions with port numbers and properties
PROTOCOLS = {
    "TCP": {
        "id": 6,
        "color": COLORS["TCP"],
        "name": "TCP",
        "description": "Transmission Control Protocol",
    },
    "UDP": {
        "id": 17,
        "color": COLORS["UDP"],
        "name": "UDP",
        "description": "User Datagram Protocol",
    },
    "ICMP": {
        "id": 1,
        "color": COLORS["ICMP"],
        "name": "ICMP",
        "description": "Internet Control Message Protocol",
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
#                              PORT DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

# Common service ports
COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    993: "IMAPS",
    995: "POP3S",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Alt",
}

# Ports commonly targeted in attacks
ATTACK_TARGET_PORTS = [22, 23, 80, 443, 445, 135, 139, 1433, 3306, 3389, 5900, 8080]

# Safe ports for normal traffic simulation
SAFE_PORTS = [80, 443, 53, 8080]

# ═══════════════════════════════════════════════════════════════════════════════
#                           ATTACK PATTERNS
# ═══════════════════════════════════════════════════════════════════════════════

# Attack type definitions for simulation
ATTACK_TYPES = {
    "NONE": {
        "name": "None",
        "intensity": 0,
        "description": "No attack",
    },
    "PORT_SCAN": {
        "name": "Port Scan",
        "intensity": 20,
        "description": "Scanning for open ports",
        "duration": 5.0,
    },
    "SYN_FLOOD": {
        "name": "SYN Flood",
        "intensity": 100,
        "description": "TCP SYN packet flood",
        "duration": 10.0,
    },
    "DDOS": {
        "name": "DDoS Attack",
        "intensity": 200,
        "description": "Distributed Denial of Service",
        "duration": 15.0,
    },
    "BRUTE_FORCE": {
        "name": "Brute Force",
        "intensity": 30,
        "description": "Password cracking attempt",
        "duration": 8.0,
    },
    "PING_FLOOD": {
        "name": "Ping Flood",
        "intensity": 150,
        "description": "ICMP echo request flood",
        "duration": 10.0,
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
#                              GAME SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Initial health of the network
INITIAL_HEALTH = 100

# Maximum health
MAX_HEALTH = 100

# Health regeneration rate per second
HEALTH_REGEN_RATE = 0.5

# Health thresholds for visual warnings
HEALTH_THRESHOLDS = {
    "CRITICAL": 20,
    "LOW": 40,
    "MEDIUM": 70,
}

# ═══════════════════════════════════════════════════════════════════════════════
#                              TIMING SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Packet capture timeout (seconds)
CAPTURE_TIMEOUT = 0.1

# Statistics update interval (seconds)
STATS_UPDATE_INTERVAL = 1.0

# How long to cache threat intel results (seconds)
THREAT_CACHE_TTL = 300

# Packet age before considered stale (seconds)
PACKET_STALE_TIME = 5.0

# ═══════════════════════════════════════════════════════════════════════════════
#                           LOGGING SETTINGS
# ═══════════════════════════════════════════════════════════════════════════════

# Log file path
LOG_FILE_PATH = "reports/packet_log.txt"

# Report file path
REPORT_FILE_PATH = "reports/security_report.txt"

# Enable/disable file logging
ENABLE_FILE_LOGGING = True

# Maximum log file size (bytes) before rotation
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10 MB

# ═══════════════════════════════════════════════════════════════════════════════
#                           DISPLAY MESSAGES
# ═══════════════════════════════════════════════════════════════════════════════

# Status messages for UI
MESSAGES = {
    "STARTING": "🚀 Initializing Packet Capture Engine...",
    "RUNNING": "🟢 System Active - Monitoring Network",
    "PAUSED": "⏸️ Capture Paused",
    "STOPPED": "🔴 Capture Stopped",
    "ERROR": "❌ Error Occurred",
    "ATTACK_DETECTED": "⚠️ ATTACK DETECTED!",
    "ATTACK_BLOCKED": "🛡️ Attack Blocked Successfully",
    "IP_BLOCKED": "🚫 IP Address Blocked",
}

# ═══════════════════════════════════════════════════════════════════════════════
#                        CONFIGURATION VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_config():
    """
    Validate configuration values on import.
    Raises ValueError if critical settings are invalid.
    """
    errors = []
    
    # Check queue size
    if MAX_QUEUE_SIZE < 10:
        errors.append("MAX_QUEUE_SIZE must be at least 10")
    
    # Check packet rates
    if NORMAL_PACKET_RATE < 1:
        errors.append("NORMAL_PACKET_RATE must be at least 1")
    
    if ATTACK_PACKET_RATE < NORMAL_PACKET_RATE:
        errors.append("ATTACK_PACKET_RATE must be >= NORMAL_PACKET_RATE")
    
    # Check IP lists are not empty
    if not WHITELISTED_IPS:
        errors.append("WHITELISTED_IPS cannot be empty")
    
    if not BLACKLISTED_IPS:
        errors.append("BLACKLISTED_IPS cannot be empty")
    
    if not SERVER_IPS:
        errors.append("SERVER_IPS cannot be empty")
    
    # Check for overlap between whitelist and blacklist
    overlap = set(WHITELISTED_IPS) & set(BLACKLISTED_IPS)
    if overlap:
        errors.append(f"IPs cannot be in both whitelist and blacklist: {overlap}")
    
    if errors:
        for error in errors:
            print(f"[CONFIG ERROR] {error}")
        return False
    
    return True


def get_config_summary():
    """
    Get a summary of current configuration.
    Useful for debugging and logging.
    """
    return {
        "simulation_mode": SIMULATION_MODE,
        "debug_mode": DEBUG_MODE,
        "interface": NETWORK_INTERFACE,
        "queue_size": MAX_QUEUE_SIZE,
        "whitelisted_ips": len(WHITELISTED_IPS),
        "blacklisted_ips": len(BLACKLISTED_IPS),
        "suspicious_ips": len(SUSPICIOUS_IPS),
        "server_ips": len(SERVER_IPS),
    }


# ═══════════════════════════════════════════════════════════════════════════════
#                              AUTO-VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

# Validate config when module is imported
if not validate_config():
    print("[CONFIG WARNING] Configuration has issues, using defaults where possible")

# Print config summary in debug mode
if DEBUG_MODE:
    print("\n[CONFIG] Configuration loaded successfully")
    summary = get_config_summary()
    for key, value in summary.items():
        print(f"  • {key}: {value}")
    print()
