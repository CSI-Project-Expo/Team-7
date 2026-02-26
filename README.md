# Packet Defender Simulation 🛡️🌐

**Packet Defender** is a high-fidelity cyber defense simulation game built with Python and Pygame. It puts you in the role of a Network Security Officer tasked with defending critical infrastructure against a barrage of sophisticated cyber attacks.

## 🚀 Overview

The simulation provides a real-time visualization of network traffic, where players must identify and mitigate various threats. From manual packet blocking to configuring advanced firewall rules, the game bridges the gap between interactive gaming and cybersecurity education.

## ✨ Key Features

- **Real-Time Packet Visualization:** Watch as TCP, UDP, and ICMP packets flow through your network, color-coded by protocol and threat level.
- **Dynamic Attack Scenarios:** Experience realistic simulations of **DDoS**, **SYN Floods**, **Port Scans**, **Brute Force**, and **DNS Amplification** attacks.
- **Firewall & Defense Engine:**
  - 17 toggleable security rules across 4 tiers
  - Real `iptables` integration (specifically designed for Kali Linux)
  - Manual "Click-to-Block" and automated defense modes
- **Advanced Monitoring:**
  - **Live Threat Graphs:** Real-time visualization of network stress and threat levels
  - **Network Heartbeat:** An ECG-style monitor tracking system health and status
  - **Cyber News Ticker:** Stay informed with in-game alerts about the evolving threat landscape
- **Resource Management:** Monitor CPU and RAM usage to ensure your defense systems don't bottleneck the network
- **Comprehensive Reporting:** Generates detailed session logs and post-mission security reports for performance analysis
- **Attack Encyclopedia:** In-game database providing educational insights into cyber threats and mitigation strategies

## 🛠️ Project Structure

- `main.py`: Central game engine and state management
- `firewall.py`: Core defense engine and `iptables` rule management
- `packet_sniffer.py`: Traffic capture and IP classification engine using Scapy
- `attack_simulator.py`: Logic for generating realistic malicious traffic patterns
- `ui_components.py`: Modular UI system for dashboards, menus, and reports
- `advanced_features.py`: Live graphs, boss battles, and power-up systems
- `unique_features.py`: Network heartbeat monitor and news ticker components
- `config.py`: Global constants, IP blacklists, and visualization settings
- `logger.py`: Centralized event logging for all security incidents

## 🚦 How to Run

### Prerequisites
- **Python 3.10+**
- **Root/Admin Privileges** (Required for real packet sniffing and `iptables` management)

### Install Dependencies
`pip install pygame scapy`

### Execution
The simulation can run in two modes based on the `SIMULATION_MODE` setting in `config.py`:

- **Simulation Mode (Default: True):** No root required. Uses generated fake packets. Run:
`python3 main.py`

- **Real Capture Mode (Set `SIMULATION_MODE = False`):** Requires root. Sniffs real network traffic. Run:
`sudo python3 main.py`

---

*Developed for Cyber Defense Simulation & Education.*
