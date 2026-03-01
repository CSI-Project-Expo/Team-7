<p align="center">
  <img src="favicon.png" alt="Packet Defender Logo" width="80"/>
</p>

<h1 align="center">🛡️ Packet Defender</h1>

<p align="center">
  <b>A high-fidelity cyber defense simulation game built with Python & Pygame</b><br/>
  <i>Defend critical infrastructure against real-world cyber attacks in real time.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Pygame-2.x-brightgreen?style=for-the-badge&logo=python&logoColor=white" alt="Pygame"/>
  <img src="https://img.shields.io/badge/Scapy-Packet%20Sniffing-blue?style=for-the-badge" alt="Scapy"/>
  <img src="https://img.shields.io/badge/Platform-Kali%20Linux-557C94?style=for-the-badge&logo=kalilinux&logoColor=white" alt="Platform"/>
  <img src="https://img.shields.io/badge/License-Educational-orange?style=for-the-badge" alt="License"/>
</p>

---

## 📖 Overview

**Packet Defender** puts you in the role of a Network Security Officer tasked with defending a simulated corporate network against waves of sophisticated cyber attacks. The game features real-time packet visualization, a configurable firewall engine with real `iptables` integration, and an engaging educational experience that bridges the gap between interactive gaming and cybersecurity training.

> ⚡ Built for the **CSI Project Expo Competition** — designed to educate, engage, and demonstrate core cybersecurity concepts in a gamified environment.

---

## ✨ Key Features

### 🎮 Core Gameplay
- **3-Wave Campaign** — Progressive difficulty across *Initial Probe*, *Coordinated Strike*, and *Advanced Threat* waves
- **Manual Click-to-Block** — Intercept hostile packets in real time by clicking them
- **Auto-Defense Mode** — Toggle AI-assisted blocking (uses CPU resources)
- **Resource Management** — Monitor CPU and RAM to prevent system overload
- **Score & Combo System** — Earn points, chain combos, and unlock multipliers
- **High Score Persistence** — Scores saved to `scores.json` across sessions

### 🔥 Attack Simulation
| Attack Type | Protocol | Severity |
|---|---|---|
| SYN Flood | TCP | 🔴 Critical |
| DDoS | Multi | 🔴 Critical |
| Port Scan | TCP | 🟡 Medium |
| Brute Force | SSH | 🟠 High |
| DNS Spoofing | UDP | 🟠 High |
| SQL Injection | HTTP | 🟠 High |
| Ping Flood | ICMP | 🟡 Medium |
| Malware Delivery | TCP | 🔴 Critical |
| Slowloris | HTTP | 🟡 Medium |
| DNS Amplification | UDP | 🟠 High |

### 🛡️ Defense Engine
- **17 Toggleable Firewall Rules** across 4 security tiers
- **Real `iptables` Integration** — When running as root on Linux, rules are applied to the actual system firewall
- **Smart Suggestion Engine** — Real-time tips based on current threats and disabled rules
- **IP Blacklist/Whitelist System** — Pre-configured threat and trusted IP databases

### 📊 Advanced Monitoring
- **Live Threat Graph** — Real-time line graph tracking threat levels over time
- **Network Heartbeat (ECG Monitor)** — Visual pulse monitor reflecting network health, with BPM and flatline detection
- **Cyber News Ticker** — Scrolling breaking news feed with simulated threat alerts
- **Live Terminal Feed** — Real-time security event log with color-coded entries
- **Adaptive Threat Indicator** — Dynamic threat level display

### 🏆 Gamification
- **Boss Battle System** — Face named bosses like *DDoS Lord*, *Malware King*, and *Botnet Queen*
- **Power-Up Collectibles** — Heal, 2x Score, Network Purge, Slow-Mo, and Auto-Block Satellite
- **Intel Collectibles** — Gather intelligence items for bonus points
- **Achievement System** — Unlock achievements for blocking milestones, wave clears, and more
- **Post-Wave Reports** — Detailed performance breakdown after each wave
- **Victory & Game Over Screens** — Comprehensive session statistics and replay option

### 🌐 Web Deployment
- **Pygbag Integration** — Play directly in the browser via WebAssembly (`index.html`)
- Pre-built `.apk` and `.tar.gz` archives for web distribution

### 📝 Reporting & Logging
- **Session Logging** — All events timestamped and saved to `logs/` directory
- **TXT & PDF Report Generation** — Professional post-session security reports via `reportlab`
- **Crash Reports** — Automatic error logging to `crash_report.txt`

### 🔍 Threat Intelligence
- **IP Reputation Checking** — Local database + optional AbuseIPDB API integration
- **Geolocation Analysis** — IP-to-location mapping for threat visualization
- **Result Caching** — Smart cache with TTL to minimize API calls
- **Rate Limiter** — Prevents API rate limit violations

---

## 🏗️ Architecture

```
Packet Defender/
├── main.py                 # 🎮 Game engine & state machine (Menu → Briefing → Play → Report → Victory)
├── firewall.py             # 🛡️ Defense engine, iptables controller, attack database, suggestion engine
├── packet_sniffer.py       # 📡 Real packet capture (Scapy) + simulation mode, IP classification
├── attack_simulator.py     # 💀 Attack pattern generation (DDoS, SYN Flood, Brute Force, etc.)
├── sprites.py              # 🎨 Packet sprites, network nodes, connection animators, particle effects
├── ui_components.py        # 🖥️ Full UI system — menus, HUD, panels, encyclopedia, reports (2300+ lines)
├── config.py               # ⚙️ Global settings, IP lists, color codes, protocol definitions
├── logger.py               # 📋 Event logging with session management and file rotation
├── report_generator.py     # 📄 TXT & PDF report generation with stats and achievements
├── threat_intel.py         # 🔍 IP reputation, caching, rate limiting, geolocation
├── advanced_features.py    # 🏅 Boss battles, power-up system, live threat graph
├── unique_features.py      # 💓 Network heartbeat monitor, cyber news ticker
├── game_enhancements.py    # 🎯 Wave system, score/combo mechanics, achievement tracking
├── index.html              # 🌐 Pygbag web deployment template
├── favicon.png             # 🖼️ Application icon
├── team-7.apk              # 📦 Pre-built web archive
└── team-7.tar.gz           # 📦 Compressed web archive
```

---

## 🚀 Getting Started

### Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.10 or higher |
| **OS** | Kali Linux (recommended for full features) |
| **Root Access** | Required for real packet capture & `iptables` rule management |

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Team-7.git
cd Team-7

# Install dependencies
pip install pygame scapy

# Optional: for PDF report generation
pip install reportlab
```

### Running the Game

#### 🎮 Simulation Mode (Default — No root required)
```bash
python main.py
```
Uses generated packets for a safe demo/presentation experience.

#### 🔬 Real Capture Mode (Kali Linux)
Edit `config.py` and set `SIMULATION_MODE = False`, then:
```bash
# Kali Linux (run as root)
sudo python3 main.py

```
Captures real network traffic using Scapy and applies real `iptables` rules.

#### 🌐 Play in Browser
Open `index.html` in a web server to play via Pygbag WebAssembly runtime.

---

## 🎮 Controls

| Key | Action |
|---|---|
| `Click` | Block hostile packets / Collect items |
| `Space` | Pause / Resume |
| `F` | Open Firewall Configuration Panel |
| `I` | Open Attack Encyclopedia |
| `A` | Toggle Auto-Defense Mode |
| `Q` | Manual Block (all hostile packets) |
| `E` | Heal Server (+25 HP) |
| `C` | Network Purge (clear all packets) |
| `R` | Restart (on Victory/Game Over) |
| `Esc` | Close panels / Quit |
| `Scroll` | Scroll through logs and panels |

---

## 🎯 How It Works

```
                    ┌──────────┐
   Packets ──────►  │  ROUTER  │
   (Real/Sim)       └────┬─────┘
                         │
                         ▼
                    ┌──────────┐     ┌─────────────────┐
                    │ FIREWALL │◄────│ 17 Defense Rules │
                    └────┬─────┘     │ + Auto-Defense   │
                         │           │ + Manual Block   │
             ┌───────────┴──────┐    └─────────────────┘
             │                  │
        ✅ Blocked         ❌ Passed
        (+Score)               │
                               ▼
                          ┌──────────┐
                          │  SERVER  │  ◄── Health: 100 HP
                          └──────────┘
                          (Takes Damage)
```

1. **Packets spawn** from the left (real captured or simulated)
2. **Travel through network nodes** — Workstation → Router → Firewall → Server
3. **Firewall inspects** each packet against enabled rules
4. **Blocked packets** award score; **leaked packets** damage the server
5. **Server health reaches 0** → Game Over | **All 3 waves cleared** → Victory

---

## 📸 Game Screens

| Screen | Description |
|---|---|
| **Main Menu** | Start game with animated UI and packet legend |
| **Mission Briefing** | Wave objectives, attack types, and strategic hints |
| **Gameplay HUD** | Health bar, threat indicator, wave progress, stats, terminal, and action buttons |
| **Firewall Panel** | Toggle 17 rules across 4 tiers with effectiveness ratings |
| **Attack Encyclopedia** | Detailed info on each attack type with counters and explanations |
| **Post-Wave Report** | Damage taken, packets blocked, intel gathered, rules active |
| **Victory Report** | Final score, high score, stats breakdown |
| **Game Over** | Mission failure summary with replay option |

---

## 🛠️ Configuration

All settings are centralized in [`config.py`](config.py):

- **`SIMULATION_MODE`** — `True` for demo, `False` for real capture
- **`DEBUG_MODE`** — Enable verbose console output
- **`NETWORK_INTERFACE`** — Set your network adapter (`eth0`, `wlan0`, `Wi-Fi`, etc.)
- **IP Lists** — Customize `WHITELISTED_IPS`, `BLACKLISTED_IPS`, `SUSPICIOUS_IPS`, `SERVER_IPS`
- **Packet Rates** — Tune `NORMAL_PACKET_RATE`, `ATTACK_PACKET_RATE`, `MAX_PACKET_RATE`
- **Colors & Themes** — Full RGB color palette for protocols, threat levels, and UI

---

## 🧰 Tech Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+** | Core language |
| **Pygame** | Game engine, rendering, input handling |
| **Scapy** | Real network packet capture and analysis |
| **iptables** | Linux firewall rule management |
| **Pygbag** | WebAssembly compilation for browser play |
| **ReportLab** | PDF report generation |
| **Threading** | Background packet capture |

---

## 👥 Team

**Team 7** — CSI Project Expo

---

## 📄 License

This project was developed for educational and competition purposes as part of the CSI Project Expo.

---

<p align="center">
  <b>⭐ Star this repo if you found it interesting!</b><br/>
  <i>Built with 💻 and ☕ by Team 7</i>
</p>
