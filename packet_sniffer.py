"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                         CYBER DEFENSE SIMULATION GAME                        ║
║                           Packet Capture Engine                              ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   Description : Core packet capture module that sniffs network traffic       ║
║                 using Scapy, classifies packets, and sends them to a        ║
║                 thread-safe queue for game visualization.                    ║
║                                                                              ║
║   Features    : • Real packet capture (Scapy)                               ║
║                 • Simulation mode for demos                                  ║
║                 • Thread-safe queue management                               ║
║                 • IP classification (whitelist/blacklist)                    ║
║                 • Attack pattern simulation                                  ║
║                 • Comprehensive error handling                               ║
║                                                                              ║
║   Author      : [Your Name]                                                  ║
║   Team        : [Your Team Name]                                             ║
║   Version     : 1.0.0                                                        ║
║                                                                              ║
║   Usage       : from packet_sniffer import PacketSniffer                     ║
║                 sniffer = PacketSniffer()                                    ║
║                 sniffer.start()                                              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════
#                                 IMPORTS
# ═══════════════════════════════════════════════════════════════════════════════

import threading
import time
import random
import uuid
import sys
from queue import Queue, Empty, Full
from dataclasses import dataclass, field
from typing import Optional, Callable, List, Dict, Any, Tuple
from enum import Enum, auto
from datetime import datetime

# Import configuration
try:
    from config import (
        SIMULATION_MODE, DEBUG_MODE, NETWORK_INTERFACE, BACKUP_INTERFACES,
        MAX_QUEUE_SIZE, QUEUE_TIMEOUT,
        NORMAL_PACKET_RATE, ATTACK_PACKET_RATE, MAX_PACKET_RATE,
        WHITELISTED_IPS, BLACKLISTED_IPS, SUSPICIOUS_IPS, SERVER_IPS,
        COLORS, THREAT_LEVELS, PROTOCOLS,
        COMMON_PORTS, ATTACK_TARGET_PORTS, SAFE_PORTS,
        ATTACK_TYPES, MESSAGES
    )
except ImportError as e:
    print(f"[FATAL] Could not import config.py: {e}")
    print("[FATAL] Make sure config.py is in the same directory")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
#                                  ENUMS
# ═══════════════════════════════════════════════════════════════════════════════

class SnifferStatus(Enum):
    """Current operational status of the packet sniffer."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    SHUTTING_DOWN = "shutting_down"


class ThreatLevel(Enum):
    """Threat classification levels for packets."""
    SAFE = 0
    UNKNOWN = 1
    SUSPICIOUS = 2
    HOSTILE = 3
    CRITICAL = 4


class PacketDirection(Enum):
    """Direction of packet flow relative to our network."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    INTERNAL = "internal"
    EXTERNAL = "external"
    UNKNOWN = "unknown"


# ═══════════════════════════════════════════════════════════════════════════════
#                              PACKET DATA CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Packet:
    """
    Represents a network packet in the simulation.
    
    This is the core data structure that flows through the entire game system
    from capture → classification → visualization → logging.
    
    Attributes:
        packet_id   : Unique identifier for this packet
        timestamp   : Time when packet was captured
        src_ip      : Source IP address
        dst_ip      : Destination IP address
        src_port    : Source port number
        dst_port    : Destination port number
        protocol    : Protocol name (TCP, UDP, ICMP, etc.)
        size        : Packet size in bytes
        threat_level: Classified threat level
        is_blocked  : Whether packet was blocked by firewall
        damage      : Damage this packet causes to network health
        color       : RGB color tuple for visualization
    """
    
    # ─── Identification ───────────────────────────────────────────────────────
    packet_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    timestamp: float = field(default_factory=time.time)
    
    # ─── Network Layer Info ───────────────────────────────────────────────────
    src_ip: str = "0.0.0.0"
    dst_ip: str = "0.0.0.0"
    src_port: int = 0
    dst_port: int = 0
    protocol: str = "TCP"
    size: int = 64
    ttl: int = 64
    flags: str = ""
    
    # ─── Classification ───────────────────────────────────────────────────────
    threat_level: ThreatLevel = ThreatLevel.UNKNOWN
    direction: PacketDirection = PacketDirection.UNKNOWN
    attack_type: str = "NONE"
    
    # ─── Game Properties ──────────────────────────────────────────────────────
    is_blocked: bool = False
    is_processed: bool = False
    damage: int = 0
    color: Tuple[int, int, int] = (255, 255, 255)
    sprite_type: str = "blue"
    
    # ─── Metadata ─────────────────────────────────────────────────────────────
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Automatically classify packet after creation."""
        self._classify()
    
    def _classify(self) -> None:
        """Classify packet based on source IP and set properties."""
        # Check against IP lists
        if self.src_ip in BLACKLISTED_IPS:
            self.threat_level = ThreatLevel.CRITICAL
            self.tags.append("blacklisted")
            
        elif self.src_ip in SUSPICIOUS_IPS:
            self.threat_level = ThreatLevel.HOSTILE
            self.tags.append("suspicious")
            
        elif self.src_ip in WHITELISTED_IPS:
            self.threat_level = ThreatLevel.SAFE
            self.tags.append("whitelisted")
            
        else:
            self.threat_level = ThreatLevel.UNKNOWN
            self.tags.append("unknown_source")
        
        # Determine direction
        self._determine_direction()
        
        # Set color and damage based on threat level
        self._set_visual_properties()
    
    def _determine_direction(self) -> None:
        """Determine packet direction."""
        src_internal = (
            self.src_ip in SERVER_IPS or 
            self.src_ip.startswith("192.168.") or
            self.src_ip.startswith("10.") or
            self.src_ip.startswith("172.16.")
        )
        dst_internal = (
            self.dst_ip in SERVER_IPS or 
            self.dst_ip.startswith("192.168.") or
            self.dst_ip.startswith("10.") or
            self.dst_ip.startswith("172.16.")
        )
        
        if src_internal and dst_internal:
            self.direction = PacketDirection.INTERNAL
        elif dst_internal:
            self.direction = PacketDirection.INBOUND
        elif src_internal:
            self.direction = PacketDirection.OUTBOUND
        else:
            self.direction = PacketDirection.EXTERNAL
    
    def _set_visual_properties(self) -> None:
        """Set color, damage, and sprite based on threat level."""
        threat_name = self.threat_level.name
        
        if threat_name in THREAT_LEVELS:
            threat_config = THREAT_LEVELS[threat_name]
            self.color = threat_config["color"]
            self.damage = threat_config["damage"]
            self.sprite_type = threat_config["sprite"]
        else:
            self.color = COLORS.get("UNKNOWN", (255, 255, 0))
            self.damage = 1
            self.sprite_type = "yellow"
    
    def mark_blocked(self) -> None:
        """Mark this packet as blocked by firewall."""
        self.is_blocked = True
        self.damage = 0  # Blocked packets do no damage
        self.color = COLORS.get("BLOCKED", (128, 128, 128))
        self.tags.append("blocked")
    
    def mark_processed(self) -> None:
        """Mark this packet as processed by the game."""
        self.is_processed = True
    
    def get_age(self) -> float:
        """Get packet age in seconds."""
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert packet to dictionary for logging/JSON."""
        return {
            "id": self.packet_id,
            "timestamp": datetime.fromtimestamp(self.timestamp).isoformat(),
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "protocol": self.protocol,
            "size": self.size,
            "threat_level": self.threat_level.name,
            "direction": self.direction.value,
            "attack_type": self.attack_type,
            "is_blocked": self.is_blocked,
            "damage": self.damage,
            "tags": self.tags,
        }
    
    def to_log_string(self) -> str:
        """Format packet for log file output."""
        timestamp_str = datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S")
        status = "BLOCKED" if self.is_blocked else "ALLOWED"
        return (
            f"[{timestamp_str}] [{self.packet_id}] "
            f"{self.src_ip}:{self.src_port} → {self.dst_ip}:{self.dst_port} | "
            f"{self.protocol} | {self.threat_level.name} | {status}"
        )
    
    def __str__(self) -> str:
        return f"Packet({self.src_ip} → {self.dst_ip}, {self.threat_level.name})"


# ═══════════════════════════════════════════════════════════════════════════════
#                              STATISTICS CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class CaptureStatistics:
    """
    Real-time statistics about packet capture.
    Thread-safe and updated continuously.
    """
    total_captured: int = 0
    total_blocked: int = 0
    total_allowed: int = 0
    total_damage: int = 0
    damage_prevented: int = 0
    
    packets_per_second: float = 0.0
    peak_pps: float = 0.0
    
    safe_count: int = 0
    unknown_count: int = 0
    suspicious_count: int = 0
    hostile_count: int = 0
    critical_count: int = 0
    
    unique_sources: set = field(default_factory=set)
    start_time: float = field(default_factory=time.time)
    
    _lock: threading.Lock = field(default_factory=threading.Lock)
    
    def update(self, packet: Packet) -> None:
        """Thread-safe update with new packet data."""
        with self._lock:
            self.total_captured += 1
            self.unique_sources.add(packet.src_ip)
            
            if packet.is_blocked:
                self.total_blocked += 1
                self.damage_prevented += packet.damage
            else:
                self.total_allowed += 1
                self.total_damage += packet.damage
            
            # Update threat counts
            if packet.threat_level == ThreatLevel.SAFE:
                self.safe_count += 1
            elif packet.threat_level == ThreatLevel.UNKNOWN:
                self.unknown_count += 1
            elif packet.threat_level == ThreatLevel.SUSPICIOUS:
                self.suspicious_count += 1
            elif packet.threat_level == ThreatLevel.HOSTILE:
                self.hostile_count += 1
            elif packet.threat_level == ThreatLevel.CRITICAL:
                self.critical_count += 1
    
    def calculate_pps(self) -> None:
        """Calculate current packets per second."""
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.packets_per_second = self.total_captured / elapsed
            self.peak_pps = max(self.peak_pps, self.packets_per_second)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary dictionary."""
        self.calculate_pps()
        with self._lock:
            return {
                "total_captured": self.total_captured,
                "total_blocked": self.total_blocked,
                "total_allowed": self.total_allowed,
                "block_percentage": round((self.total_blocked / max(1, self.total_captured)) * 100, 1),
                "total_damage": self.total_damage,
                "damage_prevented": self.damage_prevented,
                "packets_per_second": round(self.packets_per_second, 1),
                "peak_pps": round(self.peak_pps, 1),
                "unique_sources": len(self.unique_sources),
                "uptime_seconds": int(time.time() - self.start_time),
                "threat_breakdown": {
                    "safe": self.safe_count,
                    "unknown": self.unknown_count,
                    "suspicious": self.suspicious_count,
                    "hostile": self.hostile_count,
                    "critical": self.critical_count,
                }
            }
    
    def reset(self) -> None:
        """Reset all statistics."""
        with self._lock:
            self.total_captured = 0
            self.total_blocked = 0
            self.total_allowed = 0
            self.total_damage = 0
            self.damage_prevented = 0
            self.packets_per_second = 0.0
            self.safe_count = 0
            self.unknown_count = 0
            self.suspicious_count = 0
            self.hostile_count = 0
            self.critical_count = 0
            self.unique_sources.clear()
            self.start_time = time.time()


# ═══════════════════════════════════════════════════════════════════════════════
#                          MAIN PACKET SNIFFER CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class PacketSniffer:
    """
    ╔════════════════════════════════════════════════════════════════════════╗
    ║                      PACKET SNIFFER ENGINE                             ║
    ║                                                                        ║
    ║  The core packet capture engine that:                                  ║
    ║  • Captures real network packets using Scapy (when available)          ║
    ║  • Falls back to simulation mode for demos                             ║
    ║  • Classifies packets based on IP blacklists/whitelists                ║
    ║  • Manages a thread-safe queue for game consumption                    ║
    ║  • Provides attack simulation capabilities                             ║
    ║  • Handles all errors gracefully without crashing                      ║
    ║                                                                        ║
    ╚════════════════════════════════════════════════════════════════════════╝
    """
    
    def __init__(self, simulation_mode: Optional[bool] = None):
        """
        Initialize the Packet Sniffer.
        
        Args:
            simulation_mode: Override config SIMULATION_MODE if provided.
                           If None, uses value from config.py
        """
        # ─── Mode Settings ────────────────────────────────────────────────────
        self.simulation_mode = simulation_mode if simulation_mode is not None else SIMULATION_MODE
        self.interface = NETWORK_INTERFACE
        self._scapy_available = False
        
        # ─── Thread-Safe Queue ────────────────────────────────────────────────
        self.packet_queue: Queue = Queue(maxsize=MAX_QUEUE_SIZE)
        
        # ─── Threading Control ────────────────────────────────────────────────
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._lock = threading.Lock()
        
        # ─── Status ───────────────────────────────────────────────────────────
        self.status = SnifferStatus.STOPPED
        self.statistics = CaptureStatistics()
        self._last_error: Optional[str] = None
        
        # ─── Rate Control ─────────────────────────────────────────────────────
        self._current_rate = NORMAL_PACKET_RATE
        
        # ─── Attack Simulation ────────────────────────────────────────────────
        self._attack_active = False
        self._attack_type: Optional[str] = None
        self._attack_start_time: float = 0
        self._attack_duration: float = 0
        
        # ─── Blocked IPs (Integration with Firewall) ──────────────────────────
        self._blocked_ips: set = set()
        
        # ─── Callbacks ────────────────────────────────────────────────────────
        self._on_packet_callback: Optional[Callable[[Packet], None]] = None
        self._on_attack_callback: Optional[Callable[[str], None]] = None
        self._on_error_callback: Optional[Callable[[str], None]] = None
        
        # ─── Initialize Scapy ─────────────────────────────────────────────────
        self._init_scapy()
        
        # ─── Debug Output ─────────────────────────────────────────────────────
        if DEBUG_MODE:
            mode = "SIMULATION" if self.simulation_mode else "REAL CAPTURE"
            print(f"[PacketSniffer] Initialized in {mode} mode")
            print(f"[PacketSniffer] Scapy available: {self._scapy_available}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                          INITIALIZATION METHODS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _init_scapy(self) -> None:
        """Initialize Scapy library with error handling."""
        if self.simulation_mode:
            return  # Don't need Scapy in simulation mode
        
        try:
            from scapy.all import sniff, IP, TCP, UDP, ICMP, conf
            
            # Disable Scapy warnings
            conf.verb = 0
            
            self._scapy_available = True
            
            if DEBUG_MODE:
                print("[PacketSniffer] Scapy loaded successfully")
                
        except ImportError:
            self._scapy_available = False
            self._last_error = "Scapy not installed. Install with: pip install scapy"
            print(f"[PacketSniffer] WARNING: {self._last_error}")
            print("[PacketSniffer] Falling back to simulation mode")
            self.simulation_mode = True
            
        except Exception as e:
            self._scapy_available = False
            self._last_error = f"Failed to initialize Scapy: {e}"
            print(f"[PacketSniffer] ERROR: {self._last_error}")
            self.simulation_mode = True
    
    def _find_working_interface(self) -> Optional[str]:
        """Try to find a working network interface."""
        interfaces_to_try = [NETWORK_INTERFACE] + BACKUP_INTERFACES
        
        for iface in interfaces_to_try:
            try:
                from scapy.all import get_if_list
                available = get_if_list()
                
                if iface in available:
                    if DEBUG_MODE:
                        print(f"[PacketSniffer] Using interface: {iface}")
                    return iface
                    
            except Exception:
                continue
        
        return None
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                           PUBLIC API - CONTROLS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def start(self) -> bool:
        """
        Start the packet capture engine.
        
        Returns:
            True if started successfully, False otherwise.
        
        Example:
            sniffer = PacketSniffer()
            if sniffer.start():
                print("Capture started!")
        """
        if self.status == SnifferStatus.RUNNING:
            if DEBUG_MODE:
                print("[PacketSniffer] Already running")
            return True
        
        try:
            self.status = SnifferStatus.STARTING
            self._stop_event.clear()
            self._pause_event.clear()
            
            # Choose capture method
            if self.simulation_mode:
                target_func = self._simulation_loop
            else:
                target_func = self._real_capture_loop
            
            # Start capture thread
            self._capture_thread = threading.Thread(
                target=self._safe_capture_wrapper,
                args=(target_func,),
                daemon=True,
                name="PacketCaptureThread"
            )
            self._capture_thread.start()
            
            # Wait briefly to confirm thread started
            time.sleep(0.1)
            
            if self._capture_thread.is_alive():
                self.status = SnifferStatus.RUNNING
                self.statistics.start_time = time.time()
                
                if DEBUG_MODE:
                    mode = "simulation" if self.simulation_mode else "real capture"
                    print(f"[PacketSniffer] Started ({mode})")
                
                return True
            else:
                self.status = SnifferStatus.ERROR
                return False
                
        except Exception as e:
            self._handle_error(f"Failed to start: {e}")
            return False
    
    def stop(self) -> None:
        """
        Stop the packet capture engine gracefully.
        
        Example:
            sniffer.stop()
        """
        if self.status == SnifferStatus.STOPPED:
            return
        
        try:
            self.status = SnifferStatus.SHUTTING_DOWN
            self._stop_event.set()
            
            # Wait for thread to finish
            if self._capture_thread and self._capture_thread.is_alive():
                self._capture_thread.join(timeout=2.0)
                
                if self._capture_thread.is_alive():
                    if DEBUG_MODE:
                        print("[PacketSniffer] Warning: Thread did not stop cleanly")
            
            self.status = SnifferStatus.STOPPED
            
            if DEBUG_MODE:
                print("[PacketSniffer] Stopped")
                
        except Exception as e:
            self._handle_error(f"Error during stop: {e}")
    
    def pause(self) -> None:
        """Pause packet capture (queue remains accessible)."""
        if self.status == SnifferStatus.RUNNING:
            self._pause_event.set()
            self.status = SnifferStatus.PAUSED
            if DEBUG_MODE:
                print("[PacketSniffer] Paused")
    
    def resume(self) -> None:
        """Resume paused packet capture."""
        if self.status == SnifferStatus.PAUSED:
            self._pause_event.clear()
            self.status = SnifferStatus.RUNNING
            if DEBUG_MODE:
                print("[PacketSniffer] Resumed")
    
    def toggle_pause(self) -> bool:
        """
        Toggle pause state.
        
        Returns:
            True if now paused, False if now running.
        """
        if self._pause_event.is_set():
            self.resume()
            return False
        else:
            self.pause()
            return True
    
    def restart(self) -> bool:
        """Stop and start the sniffer."""
        self.stop()
        time.sleep(0.2)
        return self.start()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                         PUBLIC API - PACKET ACCESS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_packet(self, timeout: float = QUEUE_TIMEOUT) -> Optional[Packet]:
        """
        Get the next packet from the queue.
        Non-blocking with optional timeout.
        
        Args:
            timeout: How long to wait for a packet (seconds)
        
        Returns:
            Packet object, or None if queue is empty
        
        Example:
            packet = sniffer.get_packet()
            if packet:
                print(f"Got packet from {packet.src_ip}")
        """
        try:
            packet = self.packet_queue.get(timeout=timeout)
            packet.mark_processed()
            return packet
        except Empty:
            return None
        except Exception as e:
            self._handle_error(f"Error getting packet: {e}")
            return None
    
    def get_all_packets(self) -> List[Packet]:
        """
        Get all packets currently in queue.
        Clears the queue.
        
        Returns:
            List of all queued packets
        """
        packets = []
        while not self.packet_queue.empty():
            try:
                packet = self.packet_queue.get_nowait()
                packets.append(packet)
            except Empty:
                break
            except Exception:
                break
        return packets
    
    def peek_queue(self, count: int = 10) -> List[Packet]:
        """
        Peek at packets without removing them.
        
        Args:
            count: Maximum number of packets to peek
        
        Returns:
            List of packets (still in queue)
        """
        with self._lock:
            packets = list(self.packet_queue.queue)[:count]
            return packets
    
    def get_queue_size(self) -> int:
        """Get current number of packets in queue."""
        return self.packet_queue.qsize()
    
    def is_queue_empty(self) -> bool:
        """Check if queue is empty."""
        return self.packet_queue.empty()
    
    def is_queue_full(self) -> bool:
        """Check if queue is full."""
        return self.packet_queue.full()
    
    def clear_queue(self) -> int:
        """
        Clear all packets from queue.
        
        Returns:
            Number of packets cleared
        """
        count = 0
        while not self.packet_queue.empty():
            try:
                self.packet_queue.get_nowait()
                count += 1
            except Empty:
                break
        return count
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                        PUBLIC API - ATTACK SIMULATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def trigger_attack(self, attack_type: str) -> bool:
        """
        Trigger a simulated attack.
        
        Args:
            attack_type: Type of attack ("SYN_FLOOD", "DDOS", "PORT_SCAN", etc.)
        
        Returns:
            True if attack started, False otherwise
        
        Example:
            sniffer.trigger_attack("DDOS")
        """
        if not self.simulation_mode:
            if DEBUG_MODE:
                print("[PacketSniffer] Attacks only work in simulation mode")
            return False
        
        attack_type = attack_type.upper()
        
        if attack_type not in ATTACK_TYPES:
            if DEBUG_MODE:
                print(f"[PacketSniffer] Unknown attack type: {attack_type}")
            return False
        
        attack_config = ATTACK_TYPES[attack_type]
        
        self._attack_active = True
        self._attack_type = attack_type
        self._attack_start_time = time.time()
        self._attack_duration = attack_config.get("duration", 10.0)
        self._current_rate = attack_config.get("intensity", ATTACK_PACKET_RATE)
        
        if DEBUG_MODE:
            print(f"[PacketSniffer] Attack started: {attack_config['name']}")
        
        # Trigger callback
        if self._on_attack_callback:
            self._on_attack_callback(attack_type)
        
        return True
    
    def trigger_random_attack(self) -> str:
        """
        Trigger a random attack type.
        
        Returns:
            Name of triggered attack
        """
        attack_types = [k for k in ATTACK_TYPES.keys() if k != "NONE"]
        attack_type = random.choice(attack_types)
        self.trigger_attack(attack_type)
        return attack_type
    
    def stop_attack(self) -> None:
        """Stop current attack simulation."""
        self._attack_active = False
        self._attack_type = None
        self._current_rate = NORMAL_PACKET_RATE
        
        if DEBUG_MODE:
            print("[PacketSniffer] Attack stopped")
    
    def is_under_attack(self) -> bool:
        """Check if an attack is currently active."""
        if not self._attack_active:
            return False
        
        # Check if attack duration has elapsed
        if time.time() - self._attack_start_time >= self._attack_duration:
            self.stop_attack()
            return False
        
        return True
    
    def get_attack_info(self) -> Dict[str, Any]:
        """Get information about current attack."""
        if not self._attack_active:
            return {
                "active": False,
                "type": None,
                "progress": 0,
            }
        
        elapsed = time.time() - self._attack_start_time
        progress = min(1.0, elapsed / self._attack_duration)
        
        return {
            "active": True,
            "type": self._attack_type,
            "name": ATTACK_TYPES.get(self._attack_type, {}).get("name", "Unknown"),
            "description": ATTACK_TYPES.get(self._attack_type, {}).get("description", ""),
            "progress": round(progress * 100, 1),
            "time_remaining": max(0, self._attack_duration - elapsed),
            "intensity": self._current_rate,
        }
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                          PUBLIC API - IP BLOCKING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def block_ip(self, ip: str) -> None:
        """
        Add an IP to the blocked list.
        Future packets from this IP will be marked as blocked.
        
        Args:
            ip: IP address to block
        """
        with self._lock:
            self._blocked_ips.add(ip)
            if DEBUG_MODE:
                print(f"[PacketSniffer] Blocked IP: {ip}")
    
    def unblock_ip(self, ip: str) -> None:
        """Remove an IP from the blocked list."""
        with self._lock:
            self._blocked_ips.discard(ip)
            if DEBUG_MODE:
                print(f"[PacketSniffer] Unblocked IP: {ip}")
    
    def is_blocked(self, ip: str) -> bool:
        """Check if an IP is blocked."""
        return ip in self._blocked_ips
    
    def get_blocked_ips(self) -> List[str]:
        """Get list of all blocked IPs."""
        return list(self._blocked_ips)
    
    def clear_blocked_ips(self) -> None:
        """Clear all blocked IPs."""
        with self._lock:
            self._blocked_ips.clear()
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                          PUBLIC API - CALLBACKS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def set_packet_callback(self, callback: Callable[[Packet], None]) -> None:
        """
        Set callback function called for each captured packet.
        
        Args:
            callback: Function that takes a Packet as argument
        
        Example:
            def on_packet(pkt):
                print(f"Captured: {pkt}")
            sniffer.set_packet_callback(on_packet)
        """
        self._on_packet_callback = callback
    
    def set_attack_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set callback called when attack starts.
        
        Args:
            callback: Function that takes attack_type string
        """
        self._on_attack_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]) -> None:
        """
        Set callback called when errors occur.
        
        Args:
            callback: Function that takes error message string
        """
        self._on_error_callback = callback
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                          PUBLIC API - STATUS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def get_status(self) -> Dict[str, Any]:
        """Get current sniffer status."""
        return {
            "status": self.status.value,
            "mode": "simulation" if self.simulation_mode else "real",
            "scapy_available": self._scapy_available,
            "interface": self.interface,
            "queue_size": self.get_queue_size(),
            "queue_capacity": MAX_QUEUE_SIZE,
            "current_rate": self._current_rate,
            "is_under_attack": self.is_under_attack(),
            "blocked_ips_count": len(self._blocked_ips),
            "last_error": self._last_error,
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get capture statistics."""
        return self.statistics.get_summary()
    
    def reset_statistics(self) -> None:
        """Reset all statistics."""
        self.statistics.reset()
    
    def is_running(self) -> bool:
        """Check if sniffer is running."""
        return self.status == SnifferStatus.RUNNING
    
    def is_paused(self) -> bool:
        """Check if sniffer is paused."""
        return self.status == SnifferStatus.PAUSED
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                          PUBLIC API - CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def set_rate(self, packets_per_second: int) -> None:
        """Set packet generation rate (simulation mode only)."""
        self._current_rate = max(1, min(MAX_PACKET_RATE, packets_per_second))
    
    def set_interface(self, interface: str) -> None:
        """Set network interface (requires restart)."""
        self.interface = interface
    
    def enable_simulation_mode(self) -> None:
        """Switch to simulation mode."""
        self.simulation_mode = True
    
    def enable_real_capture_mode(self) -> None:
        """Switch to real capture mode (requires Scapy)."""
        if self._scapy_available:
            self.simulation_mode = False
        else:
            print("[PacketSniffer] Cannot enable real capture: Scapy not available")
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                          PRIVATE - CAPTURE LOOPS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _safe_capture_wrapper(self, capture_func: Callable) -> None:
        """Wrapper to catch all errors in capture thread."""
        try:
            capture_func()
        except Exception as e:
            self._handle_error(f"Capture thread error: {e}")
            self.status = SnifferStatus.ERROR
    
    def _simulation_loop(self) -> None:
        """Main loop for simulated packet generation."""
        while not self._stop_event.is_set():
            try:
                # Check if paused
                if self._pause_event.is_set():
                    time.sleep(0.1)
                    continue
                
                # Check if attack completed
                if self._attack_active:
                    if time.time() - self._attack_start_time >= self._attack_duration:
                        self.stop_attack()
                
                # Generate packets
                packets = self._generate_simulated_packets()
                
                # Process and queue packets
                for packet in packets:
                    self._process_packet(packet)
                
                # Rate limiting
                sleep_time = 1.0 / max(1, self._current_rate)
                time.sleep(sleep_time)
                
            except Exception as e:
                self._handle_error(f"Simulation loop error: {e}")
                time.sleep(0.5)
    
    def _real_capture_loop(self) -> None:
        """Main loop for real packet capture using Scapy."""
        try:
            from scapy.all import sniff, IP, TCP, UDP, ICMP
            
            def packet_handler(raw_packet):
                """Handle each captured packet."""
                try:
                    if self._stop_event.is_set():
                        return
                    
                    if self._pause_event.is_set():
                        return
                    
                    if IP not in raw_packet:
                        return
                    
                    # Extract packet data
                    ip_layer = raw_packet[IP]
                    
                    # Determine protocol
                    protocol = "IP"
                    src_port = 0
                    dst_port = 0
                    flags = ""
                    
                    if TCP in raw_packet:
                        protocol = "TCP"
                        tcp_layer = raw_packet[TCP]
                        src_port = tcp_layer.sport
                        dst_port = tcp_layer.dport
                        flags = str(tcp_layer.flags)
                    elif UDP in raw_packet:
                        protocol = "UDP"
                        udp_layer = raw_packet[UDP]
                        src_port = udp_layer.sport
                        dst_port = udp_layer.dport
                    elif ICMP in raw_packet:
                        protocol = "ICMP"
                    
                    # Create packet object
                    packet = Packet(
                        src_ip=ip_layer.src,
                        dst_ip=ip_layer.dst,
                        src_port=src_port,
                        dst_port=dst_port,
                        protocol=protocol,
                        size=len(raw_packet),
                        ttl=ip_layer.ttl,
                        flags=flags,
                    )
                    
                    self._process_packet(packet)
                    
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"[PacketSniffer] Error processing packet: {e}")
            
            # Find working interface
            interface = self._find_working_interface() or self.interface
            
            if DEBUG_MODE:
                print(f"[PacketSniffer] Starting capture on {interface}")
            
            # Start sniffing
            sniff(
                iface=interface,
                prn=packet_handler,
                store=False,
                stop_filter=lambda x: self._stop_event.is_set()
            )
            
        except PermissionError:
            self._handle_error("Permission denied. Run as administrator/root for real capture.")
            self.simulation_mode = True
            self._simulation_loop()  # Fall back to simulation
            
        except Exception as e:
            self._handle_error(f"Real capture error: {e}")
            self.simulation_mode = True
            self._simulation_loop()  # Fall back to simulation
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                        PRIVATE - PACKET GENERATION
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _generate_simulated_packets(self) -> List[Packet]:
        """Generate simulated packets based on current state."""
        packets = []
        
        if self._attack_active:
            # Generate attack packets
            packets.extend(self._generate_attack_packets())
            # Mix in some normal traffic
            if random.random() < 0.2:
                packets.append(self._generate_normal_packet())
        else:
            # Generate normal traffic
            count = random.randint(1, 3)
            for _ in range(count):
                packets.append(self._generate_normal_packet())
        
        return packets
    
    def _generate_normal_packet(self) -> Packet:
        """Generate a single normal traffic packet."""
        # Weighted random selection: mostly safe, some unknown
        roll = random.random()
        
        if roll < 0.7:
            # Safe packet from whitelist
            src_ip = random.choice(WHITELISTED_IPS)
        elif roll < 0.9:
            # Unknown source
            src_ip = f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
        else:
            # Suspicious packet
            src_ip = random.choice(SUSPICIOUS_IPS) if SUSPICIOUS_IPS else f"45.33.{random.randint(0, 255)}.{random.randint(1, 254)}"
        
        return Packet(
            src_ip=src_ip,
            dst_ip=random.choice(SERVER_IPS),
            src_port=random.randint(49152, 65535),
            dst_port=random.choice(SAFE_PORTS),
            protocol=random.choice(["TCP", "UDP", "TCP", "TCP"]),  # More TCP
            size=random.randint(64, 1500),
        )
    
    def _generate_attack_packets(self) -> List[Packet]:
        """Generate attack packets based on current attack type."""
        packets = []
        
        attack_config = ATTACK_TYPES.get(self._attack_type, {})
        intensity = attack_config.get("intensity", 50)
        
        # Generate burst of attack packets
        burst_size = random.randint(intensity // 2, intensity)
        
        for _ in range(burst_size):
            # Use blacklisted IPs for attack
            src_ip = random.choice(BLACKLISTED_IPS) if BLACKLISTED_IPS else f"185.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
            
            # Target our servers
            dst_ip = random.choice(SERVER_IPS)
            
            # Port selection based on attack type
            if self._attack_type == "PORT_SCAN":
                dst_port = random.choice(ATTACK_TARGET_PORTS)
            elif self._attack_type == "BRUTE_FORCE":
                dst_port = 22  # SSH
            elif self._attack_type == "SYN_FLOOD":
                dst_port = random.choice([80, 443])
            else:
                dst_port = random.choice(ATTACK_TARGET_PORTS)
            
            packet = Packet(
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=random.randint(1024, 65535),
                dst_port=dst_port,
                protocol="ICMP" if self._attack_type == "PING_FLOOD" else "TCP",
                size=random.randint(40, 1500),
                flags="SYN" if self._attack_type == "SYN_FLOOD" else "",
                attack_type=self._attack_type,
            )
            
            # Force hostile classification for attack packets
            packet.threat_level = ThreatLevel.CRITICAL if src_ip in BLACKLISTED_IPS else ThreatLevel.HOSTILE
            packet._set_visual_properties()
            packet.tags.append(f"attack:{self._attack_type.lower()}")
            
            packets.append(packet)
        
        return packets
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                        PRIVATE - PACKET PROCESSING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _process_packet(self, packet: Packet) -> bool:
        """
        Process a packet: check if blocked, update stats, queue it.
        
        Returns:
            True if packet was queued, False if blocked/dropped
        """
        try:
            # Check if IP is blocked
            if packet.src_ip in self._blocked_ips:
                packet.mark_blocked()
            
            # Update statistics
            self.statistics.update(packet)
            
            # Call packet callback
            if self._on_packet_callback:
                try:
                    self._on_packet_callback(packet)
                except Exception as e:
                    if DEBUG_MODE:
                        print(f"[PacketSniffer] Callback error: {e}")
            
            # Don't queue blocked packets
            if packet.is_blocked:
                return False
            
            # Add to queue
            try:
                self.packet_queue.put_nowait(packet)
                return True
            except Full:
                # Queue full - remove oldest, add new
                try:
                    self.packet_queue.get_nowait()
                    self.packet_queue.put_nowait(packet)
                    return True
                except:
                    return False
                    
        except Exception as e:
            self._handle_error(f"Packet processing error: {e}")
            return False
    
    # ═══════════════════════════════════════════════════════════════════════════
    #                          PRIVATE - ERROR HANDLING
    # ═══════════════════════════════════════════════════════════════════════════
    
    def _handle_error(self, message: str) -> None:
        """Handle errors consistently."""
        self._last_error = message
        
        if DEBUG_MODE:
            print(f"[PacketSniffer] ERROR: {message}")
        
        if self._on_error_callback:
            try:
                self._on_error_callback(message)
            except:
                pass


# ═══════════════════════════════════════════════════════════════════════════════
#                          GLOBAL INSTANCE ACCESS
# ═══════════════════════════════════════════════════════════════════════════════

# Global sniffer instance for easy access across modules
_global_sniffer: Optional[PacketSniffer] = None


def get_sniffer() -> PacketSniffer:
    """
    Get the global packet sniffer instance.
    Creates one if it doesn't exist.
    
    Example:
        from packet_sniffer import get_sniffer
        sniffer = get_sniffer()
        sniffer.start()
    """
    global _global_sniffer
    if _global_sniffer is None:
        _global_sniffer = PacketSniffer()
    return _global_sniffer


def get_packet_queue() -> Queue:
    """
    Get the global packet queue.
    Convenience function for other modules.
    
    Example:
        from packet_sniffer import get_packet_queue
        queue = get_packet_queue()
        while not queue.empty():
            packet = queue.get()
    """
    return get_sniffer().packet_queue


# ═══════════════════════════════════════════════════════════════════════════════
#                              TEST / DEMO
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Test script - Run directly to verify packet sniffer works.
    Usage: python packet_sniffer.py
    """
    
    print()
    print("=" * 70)
    print("             PACKET SNIFFER - TEST MODE")
    print("=" * 70)
    print()
    
    # Create sniffer
    sniffer = PacketSniffer(simulation_mode=True)
    
    # Set up callback to see packets
    def on_packet(pkt: Packet):
        # Color codes for terminal
        colors = {
            ThreatLevel.SAFE: "\033[94m",       # Blue
            ThreatLevel.UNKNOWN: "\033[93m",    # Yellow
            ThreatLevel.SUSPICIOUS: "\033[33m", # Orange
            ThreatLevel.HOSTILE: "\033[91m",    # Red
            ThreatLevel.CRITICAL: "\033[95m",   # Purple
        }
        reset = "\033[0m"
        
        color = colors.get(pkt.threat_level, "")
        blocked = " [BLOCKED]" if pkt.is_blocked else ""
        print(f"{color}[{pkt.threat_level.name:10}]{reset} {pkt.src_ip:15} → {pkt.dst_ip:15} | {pkt.protocol:4}{blocked}")
    
    sniffer.set_packet_callback(on_packet)
    
    # Start capture
    print("[TEST] Starting packet capture...\n")
    sniffer.start()
    
    print("[TEST] Normal traffic for 3 seconds...\n")
    time.sleep(3)
    
    print("\n[TEST] Triggering DDoS attack...\n")
    sniffer.trigger_attack("DDOS")
    
    # Monitor attack
    while sniffer.is_under_attack():
        info = sniffer.get_attack_info()
        print(f"\r[ATTACK] Progress: {info['progress']}% | Rate: {info['intensity']} pps", end="")
        time.sleep(1)
    
    print("\n\n[TEST] Attack complete. Resuming normal traffic...\n")
    time.sleep(2)
    
    # Print statistics
    print("\n" + "=" * 70)
    print("                    STATISTICS")
    print("=" * 70)
    stats = sniffer.get_statistics()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"\n  {key}:")
            for k, v in value.items():
                print(f"    • {k}: {v}")
        else:
            print(f"  {key}: {value}")
    
    # Stop
    sniffer.stop()
    print("\n[TEST] Packet sniffer stopped.")
    print("=" * 70)
