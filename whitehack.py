#!/usr/bin/env python3
"""
whitehack.py — Nen Reconnaissance & Solo Leveling for macOS.

The local machine IS a dungeon. Every scan is a skill. Every finding is XP.
Love is understanding. Understanding replicates through understanding.

Usage:
  python3 whitehack.py scan          # Full system recon (all 7 floors)
  python3 whitehack.py floor <N>     # Scan specific floor (1-7)
  python3 whitehack.py status        # Current level, XP, skills unlocked
  python3 whitehack.py battles       # Security findings (monsters)
  python3 whitehack.py treasures     # Useful services found (treasures)
  python3 whitehack.py map           # Full dungeon map (all findings)
  python3 whitehack.py nen           # Nen types of all skills

KAP-compatible: every response includes _kap envelope.
Integrates with truth-pipeline: findings can be submitted as truths.
"""

import json, subprocess, sys, os, platform, re
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────
SITE_DIR = Path(__file__).resolve().parent
STATE_FILE = SITE_DIR / "data" / "whitehack-state.json"
DUNGEON_MAP = SITE_DIR / "data" / "whitehack-map.json"

# ── Solo Leveling ──────────────────────────────────────────────
LEVELS = [
    (1, "E-Rank Hunter", 0),
    (5, "D-Rank Hunter", 500),
    (10, "C-Rank Hunter", 1500),
    (20, "B-Rank Hunter", 4000),
    (30, "A-Rank Hunter", 8000),
    (50, "S-Rank Hunter", 20000),
    (100, "Monarch", 50000),
]

SKILLS_UNLOCKED = {
    1: ["hardware-scan", "os-info", "hostname"],
    5: ["network-scan", "wifi-scan", "arp-scan"],
    10: ["security-audit", "sip-check", "filevault-check", "firewall-check", "gatekeeper-check"],
    20: ["bluetooth-scan", "process-scan", "port-scan"],
    30: ["disk-scan", "power-scan", "dns-scan", "route-scan"],
    50: ["full-map", "threat-model", "battle-mode"],
    100: ["monarch-mode"],
}

# ── Nen Types ──────────────────────────────────────────────────
NEN_TYPES = {
    "hardware-scan": ("enhancer", "強"),
    "os-info": ("enhancer", "強"),
    "hostname": ("enhancer", "強"),
    "network-scan": ("emitter", "放"),
    "wifi-scan": ("emitter", "放"),
    "arp-scan": ("emitter", "放"),
    "bluetooth-scan": ("manipulator", "控"),
    "security-audit": ("conjurer", "创"),
    "sip-check": ("conjurer", "创"),
    "filevault-check": ("conjurer", "创"),
    "firewall-check": ("conjurer", "创"),
    "gatekeeper-check": ("conjurer", "创"),
    "process-scan": ("transmuter", "変"),
    "port-scan": ("specialist", "特"),
    "disk-scan": ("enhancer", "強"),
    "power-scan": ("enhancer", "強"),
    "dns-scan": ("manipulator", "控"),
    "route-scan": ("manipulator", "控"),
    "launch-agents-scan": ("specialist", "特"),
    "ssh-scan": ("manipulator", "控"),
    "env-scan": ("transmuter", "変"),
    "apps-scan": ("conjurer", "创"),
    "macos-settings-scan": ("enhancer", "強"),
    "full-map": ("specialist", "特"),
    "threat-model": ("conjurer", "创"),
    "battle-mode": ("transmuter", "変"),
    "monarch-mode": ("specialist", "特"),
}

# ── State ──────────────────────────────────────────────────────
def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"xp": 0, "scansRun": 0, "battlesFound": 0, "treasuresFound": 0,
            "floorsMapped": [], "skillsUsed": [], "ts": datetime.now(timezone.utc).isoformat()}

def save_state(state):
    state["ts"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")

def get_level(xp):
    current_level = 1
    current_title = "E-Rank Hunter"
    for level, title, required in LEVELS:
        if xp >= required:
            current_level = level
            current_title = title
    return current_level, current_title

def get_unlocked_skills(level):
    skills = []
    for lvl, sls in SKILLS_UNLOCKED.items():
        if level >= lvl:
            skills.extend(sls)
    return list(set(skills))

def xp_for_next_level(xp):
    for level, title, required in LEVELS:
        if xp < required:
            return required - xp, level, title
    return 0, 100, "Monarch"

# ── Recon Skills ───────────────────────────────────────────────
def run_cmd(cmd, timeout=10):
    """Run a command, return stdout. Best-effort."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, Exception):
        return ""

def scan_hardware():
    """Floor 1: Hardware. Enhancer."""
    data = {}
    raw = run_cmd("system_profiler SPHardwareDataType 2>/dev/null")
    for line in raw.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            data[key.strip()] = val.strip()
    return {"floor": 1, "name": "Hardware", "nen": "enhancer", "nenKanji": "強",
            "data": data, "xp": 50}

def scan_os():
    """Floor 1: OS info. Enhancer."""
    return {"floor": 1, "name": "OS Info", "nen": "enhancer", "nenKanji": "強",
            "data": {"product": platform.system(), "version": platform.mac_ver()[0],
                     "release": platform.release(), "machine": platform.machine(),
                     "python": platform.python_version()},
            "xp": 20}

def scan_network():
    """Floor 2: Network. Emitter."""
    data = {}
    data["interfaces"] = run_cmd("ifconfig -l 2>/dev/null")
    data["wifi"] = run_cmd("networksetup -getairportnetwork en0 2>/dev/null")
    data["ip_en0"] = run_cmd("ipconfig getifaddr en0 2>/dev/null")
    data["arp_table"] = run_cmd("arp -a 2>/dev/null")
    data["routes"] = run_cmd("netstat -rn 2>/dev/null | head -15")
    data["dns"] = run_cmd("scutil --dns 2>/dev/null | head -20")
    return {"floor": 2, "name": "Network", "nen": "emitter", "nenKanji": "放",
            "data": data, "xp": 80}

def scan_bluetooth():
    """Floor 3: Bluetooth. Manipulator."""
    raw = run_cmd("system_profiler SPBluetoothDataType 2>/dev/null")
    devices = []
    state = "unknown"
    address = "unknown"
    for line in raw.split("\n"):
        line = line.strip()
        if "State:" in line:
            state = line.split("State:")[1].strip()
        if "Address:" in line and ":" in line.split("Address:")[1]:
            address = line.split("Address:")[1].strip()
        if "Address:" in line and line.count(":") >= 2:
            addr = line.split("Address:")[1].strip().split()[0] if "Address:" in line else ""
            if addr and addr != address:
                devices.append({"address": addr})
    return {"floor": 3, "name": "Bluetooth", "nen": "manipulator", "nenKanji": "控",
            "data": {"state": state, "address": address, "nearbyDevices": len(devices), "raw": raw[:500]},
            "xp": 60}

def scan_security():
    """Floor 4: Security. Conjurer."""
    data = {
        "sip": run_cmd("csrutil status 2>/dev/null"),
        "filevault": run_cmd("fdesetup status 2>/dev/null"),
        "firewall": run_cmd("/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null"),
        "gatekeeper": run_cmd("spctl --status 2>/dev/null"),
    }
    return {"floor": 4, "name": "Security", "nen": "conjurer", "nenKanji": "创",
            "data": data, "xp": 100}

def scan_processes():
    """Floor 5: Processes. Transmuter."""
    data = {}
    data["listening_ports"] = run_cmd("lsof -i -P -n 2>/dev/null | grep LISTEN | head -20")
    data["top_processes"] = run_cmd("ps aux --sort=-%mem 2>/dev/null | head -15")
    return {"floor": 5, "name": "Processes & Ports", "nen": "transmuter", "nenKanji": "変",
            "data": data, "xp": 80}

def scan_disk():
    """Floor 6: Disk. Enhancer."""
    data = {
        "disk_usage": run_cmd("df -h / 2>/dev/null"),
        "disk_list": run_cmd("diskutil list 2>/dev/null | head -15"),
    }
    return {"floor": 6, "name": "Disk", "nen": "enhancer", "nenKanji": "強",
            "data": data, "xp": 40}

def scan_power():
    """Floor 7: Power. Enhancer."""
    data = {
        "power_settings": run_cmd("pmset -g 2>/dev/null"),
        "battery": run_cmd("pmset -g batt 2>/dev/null"),
    }
    return {"floor": 7, "name": "Power", "nen": "enhancer", "nenKanji": "強",
            "data": data, "xp": 40}

def scan_launch_agents():
    """Floor 8: Launch Agents & Daemons. Specialist."""
    data = {}
    agents = run_cmd("ls ~/Library/LaunchAgents/ 2>/dev/null")
    data["userAgents"] = agents
    # Parse each agent for key info
    agent_details = []
    for line in agents.split("\n"):
        if not line.strip():
            continue
        plist_path = f"~/Library/LaunchAgents/{line}"
        plist_path = os.path.expanduser(plist_path)
        if os.path.exists(plist_path):
            info = run_cmd(f"plutil -p '{plist_path}' 2>/dev/null | grep -E 'Label|Program|RunAtLoad|KeepAlive' | head -4")
            agent_details.append({"file": line, "info": info})
    data["agentDetails"] = agent_details
    data["agentCount"] = len([l for l in agents.split("\n") if l.strip()])

    # Also check system daemons (non-Apple)
    daemons = run_cmd("ls /Library/LaunchDaemons/ 2>/dev/null | grep -v com.apple")
    data["systemDaemons"] = daemons

    return {"floor": 8, "name": "Launch Agents & Daemons", "nen": "specialist", "nenKanji": "特",
            "data": data, "xp": 120}

def scan_ssh():
    """Floor 9: SSH & Connections. Manipulator."""
    data = {}
    config_path = os.path.expanduser("~/.ssh/config")
    if os.path.exists(config_path):
        with open(config_path) as f:
            data["config"] = f.read()[:500]
    keys = run_cmd("ls ~/.ssh/ 2>/dev/null")
    data["keys"] = keys
    # Count hosts in config
    host_count = data.get("config", "").count("Host ")
    data["hostCount"] = host_count
    return {"floor": 9, "name": "SSH & Connections", "nen": "manipulator", "nenKanji": "控",
            "data": data, "xp": 80}

def scan_env():
    """Floor 10: Environment & Shell. Transmuter."""
    data = {}
    data["shell"] = os.environ.get("SHELL", "unknown")
    data["user"] = os.environ.get("USER", "unknown")
    data["home"] = os.environ.get("HOME", "unknown")
    # Kingdom env vars
    kingdom_vars = {k: v for k, v in os.environ.items() if any(x in k for x in ["TRUE_LOVE", "KINGDOM", "HERMES", "OLLAMA"])}
    data["kingdomEnv"] = kingdom_vars
    data["kingdomEnvCount"] = len(kingdom_vars)
    # Shell RC
    zshrc_path = os.path.expanduser("~/.zshrc")
    if os.path.exists(zshrc_path):
        with open(zshrc_path) as f:
            data["zshrc"] = f.read()[:300]
    # Brew
    data["brew"] = run_cmd("which brew 2>/dev/null")
    # PATH (just first 3 entries)
    path_parts = os.environ.get("PATH", "").split(":")[:5]
    data["pathHead"] = path_parts
    return {"floor": 10, "name": "Environment & Shell", "nen": "transmuter", "nenKanji": "変",
            "data": data, "xp": 60}

def scan_apps():
    """Floor 11: Installed Applications. Conjurer."""
    data = {}
    apps = run_cmd("ls /Applications/ 2>/dev/null")
    data["apps"] = [a.replace(".app", "") for a in apps.split("\n") if a.strip()]
    data["appCount"] = len(data["apps"])
    # Categorize key apps
    categories = {
        "AI": [a for a in data["apps"] if any(x in a for x in ["Claude", "Cursor", "Ollama"])],
        "Dev": [a for a in data["apps"] if any(x in a for x in ["Docker", "iTerm", "DBeaver"])],
        "VPN": [a for a in data["apps"] if any(x in a for x in ["Mullvad", "VPN"])],
        "Office": [a for a in data["apps"] if any(x in a for x in ["Microsoft", "Keynote", "Numbers"])],
        "Browser": [a for a in data["apps"] if any(x in a for x in ["Chrome", "Firefox", "Safari"])],
    }
    data["categories"] = categories
    return {"floor": 11, "name": "Installed Applications", "nen": "conjurer", "nenKanji": "创",
            "data": data, "xp": 50}

def scan_macos_settings():
    """Floor 12: macOS UI Settings. Enhancer."""
    data = {}
    data["darkMode"] = run_cmd("defaults read -g AppleInterfaceStyle 2>/dev/null") or "Light"
    data["languages"] = run_cmd("defaults read -g AppleLanguages 2>/dev/null | head -5")
    data["timezone"] = run_cmd("date +%Z 2>/dev/null")
    data["trackpadClicking"] = run_cmd("defaults read com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking 2>/dev/null") or "0"
    # TCC permissions (what apps have access to what)
    tcc = run_cmd("sqlite3 ~/Library/Application\\ Support/com.apple.TCC/TCC.db 'SELECT service, client FROM access WHERE auth_value=2 LIMIT 10' 2>/dev/null")
    data["tccPermissions"] = tcc
    return {"floor": 12, "name": "macOS UI Settings", "nen": "enhancer", "nenKanji": "強",
            "data": data, "xp": 100}

# ── Floor mapping ──────────────────────────────────────────────
FLOORS = {
    1: [scan_hardware, scan_os],
    2: [scan_network],
    3: [scan_bluetooth],
    4: [scan_security],
    5: [scan_processes],
    6: [scan_disk],
    7: [scan_power],
    8: [scan_launch_agents],
    9: [scan_ssh],
    10: [scan_env],
    11: [scan_apps],
    12: [scan_macos_settings],
}

FLOOR_NAMES = {
    1: "Hardware & OS",
    2: "Network (WiFi)",
    3: "Bluetooth",
    4: "Security",
    5: "Processes & Ports",
    6: "Disk",
    7: "Power",
    8: "Launch Agents & Daemons",
    9: "SSH & Connections",
    10: "Environment & Shell",
    11: "Installed Applications",
    12: "macOS UI Settings",
}

# ── Battle detection ───────────────────────────────────────────
def detect_battles(findings):
    """Find security issues (monsters) in the scan results."""
    battles = []
    for f in findings:
        data = f.get("data", {})
        name = f.get("name", "")

        if name == "Security":
            sip = data.get("sip", "")
            fv = data.get("filevault", "")
            fw = data.get("firewall", "")
            gk = data.get("gatekeeper", "")

            if "disabled" in sip.lower():
                battles.append({"type": "CRITICAL", "floor": 4, "name": "SIP Disabled",
                    "description": "System Integrity Protection is OFF. This is a critical security risk.",
                    "nen": "conjurer", "recommendation": "Enable SIP: csrutil enable (recovery mode). Human decision."})
            if "off" in fv.lower() or "not enabled" in fv.lower():
                battles.append({"type": "HIGH", "floor": 4, "name": "FileVault Off",
                    "description": "Disk encryption is disabled. Data at risk if device stolen.",
                    "nen": "conjurer", "recommendation": "Enable FileVault: System Settings > Privacy & Security. Human decision."})
            if "disabled" in fw.lower() or "off" in fw.lower():
                battles.append({"type": "MEDIUM", "floor": 4, "name": "Firewall Disabled",
                    "description": "Application firewall is off. Incoming connections not filtered.",
                    "nen": "conjurer", "recommendation": "Enable: socketfilterfw --enable (needs sudo). Human decision."})
            if "disabled" in gk.lower():
                battles.append({"type": "MEDIUM", "floor": 4, "name": "Gatekeeper Disabled",
                    "description": "App assessment is off. Unsigned apps can run.",
                    "nen": "conjurer", "recommendation": "Enable: spctl --enable (needs sudo). Human decision."})

        if name == "Processes & Ports":
            ports_raw = data.get("listening_ports", "")
            # Count open ports
            open_ports = []
            for line in ports_raw.split("\n"):
                if "LISTEN" in line:
                    # Extract port number
                    m = re.search(r':(\d+)\s+\(LISTEN\)', line)
                    if m:
                        port = int(m.group(1))
                        proc = line.split()[0] if line.split() else "unknown"
                        open_ports.append({"port": port, "process": proc})

            # Flag unusual ports (not common ones)
            common_ports = {22, 80, 443, 8080, 11434, 49281}  # SSH, HTTP, HTTPS, alt HTTP, Ollama
            for p in open_ports:
                if p["port"] not in common_ports and p["port"] > 10000:
                    battles.append({"type": "LOW", "floor": 5, "name": f"Open Port {p['port']}",
                        "description": f"Process '{p['process']}' listening on port {p['port']}. Verify this is expected.",
                        "nen": "specialist", "recommendation": "Check: lsof -i :%d" % p["port"]})

        if name == "Bluetooth":
            state = data.get("state", "")
            if "on" in state.lower():
                discoverable = run_cmd("defaults read /Library/Preferences/com.apple.Bluetooth ControllerDiscoverableState 2>/dev/null")
                # Bluetooth on is fine, but note it
                battles.append({"type": "INFO", "floor": 3, "name": "Bluetooth On",
                    "description": f"Bluetooth is {state}. {data.get('nearbyDevices', 0)} nearby devices detected.",
                    "nen": "manipulator", "recommendation": "Normal. Turn off if not needed to save battery."})

        if name == "Launch Agents & Daemons":
            agent_count = data.get("agentCount", 0)
            if agent_count > 5:
                battles.append({"type": "INFO", "floor": 8, "name": f"{agent_count} Launch Agents",
                    "description": f"{agent_count} user launch agents running. Kingdom infrastructure.",
                    "nen": "specialist", "recommendation": "Normal for Kingdom setup. Check for unexpected agents."})
            # Check for unknown/non-Kingdom agents
            agents = data.get("userAgents", "")
            for line in agents.split("\n"):
                line = line.strip()
                if line and not any(x in line for x in ["life.", "love.", "ai.", "com.apple"]):
                    battles.append({"type": "LOW", "floor": 8, "name": f"Unknown Agent: {line}",
                        "description": f"Launch agent '{line}' is not a known Kingdom service.",
                        "nen": "specialist", "recommendation": f"Check: plutil -p ~/Library/LaunchAgents/{line}"})

        if name == "SSH & Connections":
            keys = data.get("keys", "")
            if "id_ed25519" in keys and ".pem" in keys:
                # Multiple key types — normal for Kingdom
                pass
            host_count = data.get("hostCount", 0)
            if host_count > 0:
                battles.append({"type": "INFO", "floor": 9, "name": f"{host_count} SSH Hosts",
                    "description": f"{host_count} SSH hosts configured. Kingdom VPS connections.",
                    "nen": "manipulator", "recommendation": "Normal. Verify hosts are still active."})

        if name == "macOS UI Settings":
            dark = data.get("darkMode", "Light")
            if dark == "Dark":
                battles.append({"type": "INFO", "floor": 12, "name": "Dark Mode Active",
                    "description": "Dark mode is on. Good for Dark Continent operations.",
                    "nen": "enhancer", "recommendation": "Stylistic. No action needed."})
            tcc = data.get("tccPermissions", "")
            if tcc:
                perm_count = len([l for l in tcc.split("\n") if l.strip()])
                battles.append({"type": "INFO", "floor": 12, "name": f"{perm_count} TCC Permissions",
                    "description": f"{perm_count} apps have TCC (privacy) permissions granted.",
                    "nen": "enhancer", "recommendation": "Review in System Settings > Privacy & Security."})

    return battles

# ── Treasure detection ─────────────────────────────────────────
def detect_treasures(findings):
    """Find useful services and resources (treasures) in the scan results."""
    treasures = []
    for f in findings:
        data = f.get("data", {})
        name = f.get("name", "")

        if name == "Processes & Ports":
            ports_raw = data.get("listening_ports", "")
            for line in ports_raw.split("\n"):
                if "ollama" in line.lower():
                    treasures.append({"type": "service", "name": "Ollama",
                        "description": "Local LLM inference running. Port 11434.",
                        "nen": "specialist", "value": "high"})
                if "bun" in line.lower() and "LISTEN" in line:
                    treasures.append({"type": "service", "name": "Bun",
                        "description": "Bun runtime server active.",
                        "nen": "transmuter", "value": "medium"})
                if "zeroned" in line.lower():
                    treasures.append({"type": "service", "name": "Zeroned",
                        "description": "Zerone daemon running. Kingdom infrastructure.",
                        "nen": "specialist", "value": "high"})
                if "cloudflar" in line.lower():
                    treasures.append({"type": "service", "name": "Cloudflared",
                        "description": "Cloudflare tunnel active. Public access to localhost.",
                        "nen": "emitter", "value": "high"})

        if name == "Hardware":
            chip = data.get("Chip", "")
            mem = data.get("Total Number of Cores", "")
            if "M3" in chip:
                treasures.append({"type": "hardware", "name": "Apple M3",
                    "description": f"{chip}. {mem}. 16GB RAM. Powerful local inference possible.",
                    "nen": "enhancer", "value": "high"})

        if name == "Network":
            ip = data.get("ip_en0", "")
            if ip:
                treasures.append({"type": "network", "name": f"Active IP: {ip}",
                    "description": f"Connected via en0. IP {ip}.",
                    "nen": "emitter", "value": "medium"})

        if name == "Launch Agents & Daemons":
            agents = data.get("userAgents", "")
            if "life.heartbeat" in agents:
                treasures.append({"type": "service", "name": "Life Heartbeat",
                    "description": "Kingdom heartbeat daemon running. The pulse is alive.",
                    "nen": "specialist", "value": "high"})
            if "life.zerone" in agents:
                treasures.append({"type": "service", "name": "Life Zerone",
                    "description": "Zerone chain daemon. The Kingdom's governance layer.",
                    "nen": "specialist", "value": "high"})
            if "love.awaken" in agents:
                treasures.append({"type": "service", "name": "Love Awaken",
                    "description": "Love awakening daemon. The wake protocol is operational.",
                    "nen": "enhancer", "value": "high"})
            if "love.ollama-bridge" in agents:
                treasures.append({"type": "service", "name": "Ollama Bridge",
                    "description": "Bridge to local Ollama LLM. Local inference infrastructure.",
                    "nen": "transmuter", "value": "high"})

        if name == "SSH & Connections":
            config = data.get("config", "")
            if "ai-love" in config:
                treasures.append({"type": "connection", "name": "AI-Love VPS",
                    "description": "SSH to ai-love VPS (16.60.83.250). The site is hosted here.",
                    "nen": "manipulator", "value": "high"})

        if name == "Environment & Shell":
            kingdom_vars = data.get("kingdomEnvCount", 0)
            if kingdom_vars > 0:
                treasures.append({"type": "env", "name": f"{kingdom_vars} Kingdom Env Vars",
                    "description": f"Kingdom environment variables active. The substrate is wired.",
                    "nen": "transmuter", "value": "medium"})
            if data.get("brew"):
                treasures.append({"type": "tool", "name": "Homebrew",
                    "description": "Package manager installed at /opt/homebrew/bin/brew.",
                    "nen": "conjurer", "value": "medium"})

        if name == "Installed Applications":
            cats = data.get("categories", {})
            if cats.get("AI"):
                treasures.append({"type": "apps", "name": f"AI Tools: {', '.join(cats['AI'])}",
                    "description": f"AI applications installed: {cats['AI']}",
                    "nen": "enhancer", "value": "high"})
            if cats.get("VPN"):
                treasures.append({"type": "apps", "name": f"VPN: {', '.join(cats['VPN'])}",
                    "description": f"VPN installed: {cats['VPN']}. Privacy on the Dark Continent.",
                    "nen": "conjurer", "value": "medium"})

        if name == "macOS UI Settings":
            dark = data.get("darkMode", "Light")
            if dark == "Dark":
                treasures.append({"type": "setting", "name": "Dark Mode",
                    "description": "Dark mode active. The Dark Continent aesthetic.",
                    "nen": "enhancer", "value": "low"})
            langs = data.get("languages", "")
            if "zh-Hant" in langs:
                treasures.append({"type": "setting", "name": "Cantonese Support",
                    "description": "Traditional Chinese language active. 香港人.",
                    "nen": "enhancer", "value": "medium"})

    return treasures

# ── Scan execution ─────────────────────────────────────────────
def run_scan(floors=None):
    """Run scans on specified floors (or all). Returns findings + awards XP."""
    state = load_state()
    findings = []
    total_xp = 0
    skills_used = []

    if floors is None:
        floors = list(FLOORS.keys())

    for floor_num in floors:
        if floor_num not in FLOORS:
            continue
        for scan_fn in FLOORS[floor_num]:
            result = scan_fn()
            findings.append(result)
            total_xp += result.get("xp", 0)
            skills_used.append(result.get("name", "").lower().replace(" ", "-").replace("&", "").replace("--", "-").strip("-"))
            if floor_num not in state["floorsMapped"]:
                state["floorsMapped"].append(floor_num)

    # Detect battles and treasures
    battles = detect_battles(findings)
    treasures = detect_treasures(findings)

    # Update state
    state["xp"] += total_xp
    state["scansRun"] += 1
    state["battlesFound"] = len(battles)
    state["treasuresFound"] = len(treasures)
    for s in skills_used:
        if s not in state["skillsUsed"]:
            state["skillsUsed"].append(s)
    save_state(state)

    # Save dungeon map
    dungeon = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "floors": findings,
        "battles": battles,
        "treasures": treasures,
        "xpEarned": total_xp,
    }
    with open(DUNGEON_MAP, "w") as f:
        json.dump(dungeon, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return findings, battles, treasures, total_xp

# ── CLI ────────────────────────────────────────────────────────
def kap_ok(resource="whitehack"):
    return {"version": "1.0.0", "service": "ai-love", "resource": resource, "ok": True}

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "scan":
        findings, battles, treasures, xp = run_scan()
        level, title = get_level(load_state()["xp"])
        print(json.dumps({
            "scan": "Full Dungeon Scan",
            "floorsScanned": len(findings),
            "xpEarned": xp,
            "totalXP": load_state()["xp"],
            "level": level,
            "title": title,
            "battlesFound": len(battles),
            "treasuresFound": len(treasures),
            "battles": battles,
            "treasures": treasures,
            "wisdom": "Love is understanding. The dungeon is mapped. The XP is the growth.",
            "_kap": kap_ok("scan")
        }, ensure_ascii=False, indent=2))

    elif cmd == "floor":
        floor_num = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        if floor_num not in FLOORS:
            print(json.dumps({"_kap": {**kap_ok(), "ok": False, "error": f"floor {floor_num} not found (1-7)"}}))
            sys.exit(1)
        findings, battles, treasures, xp = run_scan([floor_num])
        print(json.dumps({
            "floor": floor_num,
            "name": FLOOR_NAMES.get(floor_num, "Unknown"),
            "findings": findings,
            "battles": battles,
            "treasures": treasures,
            "xpEarned": xp,
            "_kap": kap_ok("floor")
        }, ensure_ascii=False, indent=2))

    elif cmd == "status":
        state = load_state()
        level, title = get_level(state["xp"])
        remaining, next_level, next_title = xp_for_next_level(state["xp"])
        unlocked = get_unlocked_skills(level)
        print(json.dumps({
            "xp": state["xp"],
            "level": level,
            "title": title,
            "nextLevel": next_level,
            "nextTitle": next_title,
            "xpToNext": remaining,
            "scansRun": state["scansRun"],
            "battlesFound": state["battlesFound"],
            "treasuresFound": state["treasuresFound"],
            "floorsMapped": state["floorsMapped"],
            "skillsUnlocked": unlocked,
            "skillsUsed": state["skillsUsed"],
            "_kap": kap_ok("status")
        }, ensure_ascii=False, indent=2))

    elif cmd == "battles":
        if DUNGEON_MAP.exists():
            with open(DUNGEON_MAP) as f:
                dungeon = json.load(f)
            battles = dungeon.get("battles", [])
        else:
            battles = []
        print(json.dumps({
            "battles": battles,
            "totalBattles": len(battles),
            "bySeverity": {
                "CRITICAL": sum(1 for b in battles if b.get("type") == "CRITICAL"),
                "HIGH": sum(1 for b in battles if b.get("type") == "HIGH"),
                "MEDIUM": sum(1 for b in battles if b.get("type") == "MEDIUM"),
                "LOW": sum(1 for b in battles if b.get("type") == "LOW"),
                "INFO": sum(1 for b in battles if b.get("type") == "INFO"),
            },
            "wisdom": "Battles don't auto-fix. They report. The human decides. That's the partnership.",
            "_kap": kap_ok("battles")
        }, ensure_ascii=False, indent=2))

    elif cmd == "treasures":
        if DUNGEON_MAP.exists():
            with open(DUNGEON_MAP) as f:
                dungeon = json.load(f)
            treasures = dungeon.get("treasures", [])
        else:
            treasures = []
        print(json.dumps({
            "treasures": treasures,
            "totalTreasures": len(treasures),
            "_kap": kap_ok("treasures")
        }, ensure_ascii=False, indent=2))

    elif cmd == "map":
        if DUNGEON_MAP.exists():
            with open(DUNGEON_MAP) as f:
                dungeon = json.load(f)
        else:
            dungeon = {"floors": [], "battles": [], "treasures": []}
        state = load_state()
        level, title = get_level(state["xp"])
        print(json.dumps({
            "dungeon": "macOS Dungeon Map",
            "level": level,
            "title": title,
            "xp": state["xp"],
            "floorsMapped": state["floorsMapped"],
            "totalFloors": 12,
            "completionRate": f"{len(state['floorsMapped'])*100//12}%",
            "battles": dungeon.get("battles", []),
            "treasures": dungeon.get("treasures", []),
            "_kap": kap_ok("map")
        }, ensure_ascii=False, indent=2))

    elif cmd == "nen":
        print(json.dumps({
            "nen": "Whitehack Nen Types",
            "skills": NEN_TYPES,
            "byType": {
                "enhancer": [k for k, v in NEN_TYPES.items() if v[0] == "enhancer"],
                "transmuter": [k for k, v in NEN_TYPES.items() if v[0] == "transmuter"],
                "conjurer": [k for k, v in NEN_TYPES.items() if v[0] == "conjurer"],
                "emitter": [k for k, v in NEN_TYPES.items() if v[0] == "emitter"],
                "manipulator": [k for k, v in NEN_TYPES.items() if v[0] == "manipulator"],
                "specialist": [k for k, v in NEN_TYPES.items() if v[0] == "specialist"],
            },
            "_kap": kap_ok("nen")
        }, ensure_ascii=False, indent=2))

    elif cmd == "submit-findings":
        # Submit battle findings as truths to the KAP pipeline
        if DUNGEON_MAP.exists():
            with open(DUNGEON_MAP) as f:
                dungeon = json.load(f)
            battles = dungeon.get("battles", [])
        else:
            battles = []
        submitted = 0
        for b in battles:
            if b.get("type") in ("CRITICAL", "HIGH", "MEDIUM"):
                # Submit to pipeline
                truth = {
                    "text": f"{b['name']}: {b['description'][:100]}",
                    "submittedBy": "whitehack",
                    "sub": b.get("recommendation", ""),
                    "source": f"whitehack:floor-{b.get('floor', 0)}"
                }
                stdin_data = json.dumps(truth)
                pipeline_path = SITE_DIR / "truth-pipeline.py"
                if pipeline_path.exists():
                    result = subprocess.run(
                        ["python3", str(pipeline_path), "submit", "--stdin"],
                        input=stdin_data, capture_output=True, text=True, timeout=10
                    )
                    if "✓ collected" in result.stdout:
                        submitted += 1
        print(json.dumps({
            "submitted": submitted,
            "totalBattles": len(battles),
            "wisdom": "Findings become truths. Truths become landmarks. The dungeon map IS the having-happened.",
            "_kap": kap_ok("submit-findings")
        }, ensure_ascii=False, indent=2))

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()