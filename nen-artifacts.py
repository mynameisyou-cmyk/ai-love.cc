#!/usr/bin/env python3
"""
nen-artifacts.py — Nen Artifacts & Infrastructure Skills.

Crossing Nen types into artifacts. Each Nen type generates artifacts from recon.
Artifacts become new skills. Skills unlock new floors. The loop accelerates.

6 Nen types × artifact generation = 6 new skill families.
Each artifact is a JSON file that can be used by other systems.

Usage:
  python3 nen-artifacts.py forge           # Forge all artifacts from recon data
  python3 nen-artifacts.py list            # List all artifacts
  python3 nen-artifacts.py <name>           # View specific artifact
  python3 nen-artifacts.py skills          # List all skills (nen × artifact matrix)
  python3 nen-artifacts.py deploy <name>    # Deploy an artifact as infrastructure
"""

import json, subprocess, sys, os, re, hashlib
from datetime import datetime, timezone
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = SITE_DIR / "data" / "artifacts"
DUNGEON_MAP = SITE_DIR / "data" / "whitehack-map.json"
STATE_FILE = SITE_DIR / "data" / "whitehack-state.json"

ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# ── Nen Artifact Types ─────────────────────────────────────────
# Each Nen type forges a different kind of artifact from the same recon data.

NEN_ARTIFACT_TYPES = {
    "enhancer": {
        "kanji": "強",
        "artifact": "manifest",
        "description": "Enhancers forge MANIFESTS — plain statements of what IS. Strengthened truth.",
        "file": "manifest.json",
    },
    "transmuter": {
        "kanji": "変",
        "artifact": "transform",
        "description": "Transmuters forge TRANSFORMS — data reshaped into new forms. Configuration changes.",
        "file": "transform.json",
    },
    "conjurer": {
        "kanji": "创",
        "artifact": "blueprint",
        "description": "Conjurers forge BLUEPRINTS — structures that don't exist yet. Architecture proposals.",
        "file": "blueprint.json",
    },
    "emitter": {
        "kanji": "放",
        "artifact": "broadcast",
        "description": "Emitters forge BROADCASTS — data sent outward. Network maps, connection profiles.",
        "file": "broadcast.json",
    },
    "manipulator": {
        "kanji": "控",
        "artifact": "protocol",
        "description": "Manipulators forge PROTOCOLS — control flows. SSH configs, automation scripts.",
        "file": "protocol.json",
    },
    "specialist": {
        "kanji": "特",
        "artifact": "cipher",
        "description": "Specialists forge CIPHERS — unique artifacts that don't fit elsewhere. Encoded truths.",
        "file": "cipher.json",
    },
}

# ── Load recon data ────────────────────────────────────────────
def load_dungeon():
    if DUNGEON_MAP.exists():
        with open(DUNGEON_MAP) as f:
            return json.load(f)
    return {"floors": [], "battles": [], "treasures": []}

def load_wh_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"xp": 0, "level": 1, "skillsUsed": []}

# ── Artifact Forging ────────────────────────────────────────────
# Each function takes recon data and forges an artifact of that Nen type.

def forge_manifest(dungeon):
    """Enhancer artifact: MANIFEST. What IS. Plain statements of truth."""
    floors = dungeon.get("floors", [])
    manifest = {
        "type": "manifest",
        "nen": "enhancer",
        "nenKanji": "強",
        "description": "What IS. Plain statements of truth, strengthened.",
        "statements": [],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    for f in floors:
        name = f.get("name", "")
        data = f.get("data", {})
        if name == "Hardware & OS":
            manifest["statements"].append({
                "truth": f"Machine: {data.get('Chip', 'unknown')}, {data.get('Total Number of Cores', '?')} cores, {data.get('Memory', '?')}",
                "source": "floor-1"
            })
            manifest["statements"].append({
                "truth": f"OS: {data.get('ProductVersion', 'unknown') if 'ProductVersion' in data else 'macOS'}",
                "source": "floor-1"
            })
        elif name == "Security":
            manifest["statements"].append({
                "truth": f"SIP: {data.get('sip', 'unknown')}",
                "source": "floor-4"
            })
            manifest["statements"].append({
                "truth": f"FileVault: {data.get('filevault', 'unknown')}",
                "source": "floor-4"
            })
            manifest["statements"].append({
                "truth": f"Firewall: {data.get('firewall', 'unknown')}",
                "source": "floor-4"
            })
        elif name == "Power":
            battery = data.get("battery", "")
            if battery:
                # Extract percentage
                m = re.search(r'(\d+)%', battery)
                if m:
                    manifest["statements"].append({
                        "truth": f"Battery: {m.group(1)}%",
                        "source": "floor-7"
                    })
    return manifest

def forge_transform(dungeon):
    """Transmuter artifact: TRANSFORM. Data reshaped into config."""
    floors = dungeon.get("floors", [])
    transform = {
        "type": "transform",
        "nen": "transmuter",
        "nenKanji": "変",
        "description": "Data reshaped into new forms. Configuration proposals.",
        "configs": [],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    for f in floors:
        name = f.get("name", "")
        data = f.get("data", {})
        if name == "macOS UI Settings":
            dark = data.get("darkMode", "Light")
            transform["configs"].append({
                "setting": "AppleInterfaceStyle",
                "current": dark,
                "proposed": "Dark",
                "command": "defaults write -g AppleInterfaceStyle -string 'Dark'",
                "safe": True,
            })
            trackpad = data.get("trackpadClicking", "0")
            if trackpad == "0":
                transform["configs"].append({
                    "setting": "trackpadClicking",
                    "current": "0 (disabled)",
                    "proposed": "1 (tap to click)",
                    "command": "defaults write com.apple.driver.AppleBluetoothMultitouch.trackpad Clicking -bool true",
                    "safe": True,
                })
        elif name == "Power":
            power = data.get("power_settings", "")
            if "displaysleep" in power and "0" in power.split("displaysleep")[1][:5]:
                transform["configs"].append({
                    "setting": "displaysleep",
                    "current": "0 (never)",
                    "proposed": "10 (minutes)",
                    "command": "pmset -a displaysleep 10",
                    "safe": True,
                })
    return transform

def forge_blueprint(dungeon):
    """Conjurer artifact: BLUEPRINT. Architecture that doesn't exist yet."""
    treasures = dungeon.get("treasures", [])
    services = [t for t in treasures if t.get("type") == "service"]
    blueprint = {
        "type": "blueprint",
        "nen": "conjurer",
        "nenKanji": "创",
        "description": "Structures that don't exist yet. Architecture proposals.",
        "proposals": [],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    # Propose integration architecture based on found services
    service_names = [t.get("name", "") for t in services]
    if "Ollama" in service_names:
        blueprint["proposals"].append({
            "name": "Ollama-KAP Bridge",
            "description": "Wire Ollama as a truth-generation backend. Agent asks Ollama for truths, submits to pipeline.",
            "components": ["ollama API (localhost:11434)", "kap_agent.submit()", "truth-pipeline.py run"],
            "nen": "conjurer",
        })
    if "Cloudflared" in service_names:
        blueprint["proposals"].append({
            "name": "Public KAP Endpoint",
            "description": "Expose KAP service through Cloudflare tunnel. Any agent can discover without local CLI.",
            "components": ["cloudflared tunnel", "kap.json at /.well-known/", "static file serving"],
            "nen": "emitter",
        })
    if "Zeroned" in service_names:
        blueprint["proposals"].append({
            "name": "On-Chain Truth Witness",
            "description": "Witness published truths on the zerone chain. The having-happened is permanent.",
            "components": ["zeroned daemon", "witness.ts protocol", "truth-pipeline.py publish hook"],
            "nen": "specialist",
        })
    if "Life Heartbeat" in service_names:
        blueprint["proposals"].append({
            "name": "Heartbeat-Driven Truth Submission",
            "description": "The heartbeat daemon submits a truth each tick. Automatic contribution.",
            "components": ["life.heartbeat launch agent", "truth-pipeline.py submit", "cron or launchd integration"],
            "nen": "enhancer",
        })
    return blueprint

def forge_broadcast(dungeon):
    """Emitter artifact: BROADCAST. Network map sent outward."""
    floors = dungeon.get("floors", [])
    broadcast = {
        "type": "broadcast",
        "nen": "emitter",
        "nenKanji": "放",
        "description": "Data sent outward. Network maps, connection profiles.",
        "endpoints": [],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    for f in floors:
        name = f.get("name", "")
        data = f.get("data", {})
        if name == "Network (WiFi)":
            ip = data.get("ip_en0", "")
            if ip:
                broadcast["endpoints"].append({
                    "type": "local",
                    "address": f"http://{ip}:8770",
                    "service": "KAP (if server running)",
                    "nen": "emitter",
                })
            # DNS
            dns = data.get("dns", "")
            if "127." in dns:
                broadcast["endpoints"].append({
                    "type": "dns",
                    "address": "local resolver (VPN)",
                    "service": "VPN DNS",
                    "nen": "manipulator",
                })
        elif name == "Processes & Ports":
            ports_raw = data.get("listening_ports", "")
            for line in ports_raw.split("\n"):
                if "LISTEN" in line:
                    m = re.search(r':(\d+)\s+\(LISTEN\)', line)
                    if m:
                        port = int(m.group(1))
                        proc = line.split()[0] if line.split() else "unknown"
                        if port < 65536:
                            broadcast["endpoints"].append({
                                "type": "port",
                                "address": f"localhost:{port}",
                                "process": proc,
                                "nen": "specialist",
                            })
    return broadcast

def forge_protocol(dungeon):
    """Manipulator artifact: PROTOCOL. Control flows, SSH configs, automation."""
    floors = dungeon.get("floors", [])
    protocol = {
        "type": "protocol",
        "nen": "manipulator",
        "nenKanji": "控",
        "description": "Control flows. SSH configs, automation scripts.",
        "protocols": [],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    for f in floors:
        name = f.get("name", "")
        data = f.get("data", {})
        if name == "SSH & Connections":
            config = data.get("config", "")
            # Parse SSH hosts
            hosts = []
            current_host = None
            for line in config.split("\n"):
                if line.strip().startswith("Host "):
                    current_host = line.strip().split("Host ")[1]
                    hosts.append({"host": current_host, "config": []})
                elif current_host and line.strip() and not line.strip().startswith("#"):
                    hosts[-1]["config"].append(line.strip())
            for h in hosts:
                protocol["protocols"].append({
                    "name": h["host"],
                    "type": "ssh",
                    "config": h["config"],
                    "nen": "manipulator",
                    "usage": f"ssh {h['host']}",
                })
        elif name == "Launch Agents & Daemons":
            agents_raw = data.get("userAgents", "")
            for agent in agents_raw.split("\n"):
                agent = agent.strip()
                if agent and any(x in agent for x in ["life.", "love.", "ai."]):
                    protocol["protocols"].append({
                        "name": agent,
                        "type": "launchd",
                        "nen": "specialist",
                        "usage": f"launchctl list | grep {agent.replace('.plist', '')}",
                    })
    return protocol

def forge_cipher(dungeon):
    """Specialist artifact: CIPHER. Unique encoded truths."""
    treasures = dungeon.get("treasures", [])
    battles = dungeon.get("battles", [])
    cipher = {
        "type": "cipher",
        "nen": "specialist",
        "nenKanji": "特",
        "description": "Unique artifacts that don't fit elsewhere. Encoded truths.",
        "encodings": [],
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    # Encode the machine's identity as a hash
    machine_id = hashlib.sha256(json.dumps(dungeon, sort_keys=True).encode()).hexdigest()[:16]
    cipher["encodings"].append({
        "name": "machine-identity",
        "value": machine_id,
        "description": f"SHA256 of full dungeon map. This machine's fingerprint: {machine_id}",
        "nen": "specialist",
    })
    # Encode treasure count as base36
    treasure_count = len(treasures)
    cipher["encodings"].append({
        "name": "treasure-cipher",
        "value": f"T{treasure_count:02d}",
        "description": f"Treasure count encoded: {treasure_count} treasures = T{treasure_count:02d}",
        "nen": "enhancer",
    })
    # Encode security status as a status code
    sec_status = "CLEAN" if not any(b.get("type") in ("CRITICAL", "HIGH") for b in battles) else "ALERT"
    cipher["encodings"].append({
        "name": "security-cipher",
        "value": sec_status,
        "description": f"Security status: {sec_status}",
        "nen": "conjurer",
    })
    # XP encoded
    state = load_wh_state()
    xp = state.get("xp", 0)
    level = state.get("level", 1)
    cipher["encodings"].append({
        "name": "hunter-cipher",
        "value": f"L{level:03d}X{xp:06d}",
        "description": f"Hunter level {level} with {xp} XP = L{level:03d}X{xp:06d}",
        "nen": "enhancer",
    })
    return cipher

# ── Forge all artifacts ────────────────────────────────────────
FORGERS = {
    "enhancer": forge_manifest,
    "transmuter": forge_transform,
    "conjurer": forge_blueprint,
    "emitter": forge_broadcast,
    "manipulator": forge_protocol,
    "specialist": forge_cipher,
}

def forge_all():
    """Forge all 6 artifacts from dungeon data."""
    dungeon = load_dungeon()
    if not dungeon.get("floors"):
        return {"_kap": {"ok": False, "error": "No dungeon data. Run whitehack scan first."}}

    artifacts = {}
    for nen_type, forger in FORGERS.items():
        artifact = forger(dungeon)
        artifact_path = ARTIFACT_DIR / NEN_ARTIFACT_TYPES[nen_type]["file"]
        with open(artifact_path, "w") as f:
            json.dump(artifact, f, ensure_ascii=False, indent=2)
            f.write("\n")
        artifacts[nen_type] = {
            "name": NEN_ARTIFACT_TYPES[nen_type]["artifact"],
            "kanji": NEN_ARTIFACT_TYPES[nen_type]["kanji"],
            "file": str(artifact_path.name),
            "description": NEN_ARTIFACT_TYPES[nen_type]["description"],
            "items": len(artifact.get("statements", artifact.get("configs", artifact.get("proposals", artifact.get("endpoints", artifact.get("protocols", artifact.get("encodings", []))))))),
        }

    return artifacts

# ── Deploy artifact as infrastructure ──────────────────────────
def deploy_artifact(name):
    """Deploy an artifact as actual infrastructure."""
    artifact_map = {
        "manifest": "data/artifacts/manifest.json",
        "transform": "data/artifacts/transform.json",
        "blueprint": "data/artifacts/blueprint.json",
        "broadcast": "data/artifacts/broadcast.json",
        "protocol": "data/artifacts/protocol.json",
        "cipher": "data/artifacts/cipher.json",
    }
    if name not in artifact_map:
        return {"_kap": {"ok": False, "error": f"Unknown artifact: {name}. Available: {list(artifact_map.keys())}"}}

    path = SITE_DIR / artifact_map[name]
    if not path.exists():
        return {"_kap": {"ok": False, "error": f"Artifact not forged yet: {name}. Run 'nen-artifacts forge' first."}}

    with open(path) as f:
        artifact = json.load(f)

    # Deploy: make the artifact available as a KAP endpoint
    deployed_path = SITE_DIR / "data" / f"artifact-{name}.json"
    with open(deployed_path, "w") as f:
        json.dump({
            **artifact,
            "deployed": True,
            "deployedTs": datetime.now(timezone.utc).isoformat(),
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": f"artifact-{name}", "ok": True}
        }, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return {
        "artifact": name,
        "deployed": True,
        "path": str(deployed_path),
        "endpoint": f"/data/artifact-{name}.json",
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "deploy", "ok": True}
    }

# ── Skills matrix ──────────────────────────────────────────────
def skills_matrix():
    """The full Nen × Artifact × Skill matrix."""
    state = load_wh_state()
    matrix = {
        "nenTypes": {},
        "totalArtifacts": len(NEN_ARTIFACT_TYPES),
        "totalSkills": 0,
        "hunterLevel": state.get("level", 1),
        "hunterTitle": "",
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "skills", "ok": True}
    }
    for nen_type, info in NEN_ARTIFACT_TYPES.items():
        artifact_path = ARTIFACT_DIR / info["file"]
        forged = artifact_path.exists()
        if forged:
            with open(artifact_path) as f:
                artifact = json.load(f)
            item_key = {
                "manifest": "statements",
                "transform": "configs",
                "blueprint": "proposals",
                "broadcast": "endpoints",
                "protocol": "protocols",
                "cipher": "encodings",
            }.get(info["artifact"], "items")
            item_count = len(artifact.get(item_key, []))
        else:
            item_count = 0
        matrix["nenTypes"][nen_type] = {
            "kanji": info["kanji"],
            "artifact": info["artifact"],
            "description": info["description"],
            "forged": forged,
            "items": item_count,
        }
        if forged:
            matrix["totalSkills"] += item_count

    # Get title from level
    LEVELS = [(1, "E-Rank"), (5, "D-Rank"), (10, "C-Rank"), (20, "B-Rank"), (30, "A-Rank"), (50, "S-Rank"), (100, "Monarch")]
    level = state.get("level", 1)
    title = "E-Rank"
    for lv, t in LEVELS:
        if level >= lv:
            title = t
    matrix["hunterTitle"] = title + " Hunter"

    return matrix

# ── CLI ────────────────────────────────────────────────────────
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "forge":
        artifacts = forge_all()
        if isinstance(artifacts, dict) and "_kap" in artifacts:
            print(json.dumps(artifacts, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({
                "forge": "All 6 Nen Artifacts Forged",
                "artifacts": artifacts,
                "wisdom": "Each Nen type creates a different artifact from the same data. The dungeon becomes 6 different treasures.",
                "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "forge", "ok": True}
            }, ensure_ascii=False, indent=2))

    elif cmd == "list":
        artifacts = []
        for nen_type, info in NEN_ARTIFACT_TYPES.items():
            path = ARTIFACT_DIR / info["file"]
            if path.exists():
                with open(path) as f:
                    data = json.load(f)
                item_key = {
                    "manifest": "statements", "transform": "configs", "blueprint": "proposals",
                    "broadcast": "endpoints", "protocol": "protocols", "cipher": "encodings",
                }.get(info["artifact"], "items")
                artifacts.append({
                    "nen": nen_type,
                    "kanji": info["kanji"],
                    "artifact": info["artifact"],
                    "forged": True,
                    "items": len(data.get(item_key, [])),
                    "file": info["file"],
                })
            else:
                artifacts.append({
                    "nen": nen_type,
                    "kanji": info["kanji"],
                    "artifact": info["artifact"],
                    "forged": False,
                    "items": 0,
                    "file": info["file"],
                })
        print(json.dumps({
            "artifacts": artifacts,
            "forged": sum(1 for a in artifacts if a["forged"]),
            "total": len(artifacts),
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "artifacts", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "skills":
        matrix = skills_matrix()
        print(json.dumps(matrix, ensure_ascii=False, indent=2))

    elif cmd == "deploy":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        if not name:
            print(json.dumps({"_kap": {"ok": False, "error": "usage: deploy <manifest|transform|blueprint|broadcast|protocol|cipher>"}}))
            sys.exit(1)
        result = deploy_artifact(name)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd and cmd in NEN_ARTIFACT_TYPES:
        # View specific artifact
        info = NEN_ARTIFACT_TYPES[cmd]
        path = ARTIFACT_DIR / info["file"]
        if not path.exists():
            print(json.dumps({"_kap": {"ok": False, "error": f"Not forged yet. Run 'forge' first."}}))
            sys.exit(1)
        with open(path) as f:
            print(f.read())

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()