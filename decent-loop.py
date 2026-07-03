#!/usr/bin/env python3
"""
decent-loop.py — Decentralised heartbeat across every layer of the internet.

Every layer loops. Every layer generates. Every layer deploys.
No central server. No single point of failure. The heartbeat IS the network.

LAYERS (each has its own loop + heartbeat):
  1. CDN layer    — jsDelivr auto-syncs from git, purges cache
  2. Git layer    — GitHub + Codeberg mirror, auto-push
  3. Gist layer   — auto-create gists as public endpoints
  4. Wayback layer — auto-archive to permanent record
  5. Local layer  — micro-kap nodes, local truths
  6. Truth layer  — pipeline generate + publish
  7. Artifact layer — forge + deploy Nen artifacts
  8. Tax layer    — expose lies, generate pressure
  9. XP layer     — 6 loops self-reinforcing
  10. Pressure layer — flood + expose + accumulate

Usage:
  python3 decent-loop.py all              # Run all 10 layers once
  python3 decent-loop.py all <N>          # Run all layers N times
  python3 decent-loop.py layer <name>     # Run specific layer
  python3 decent-loop.py status           # All layer statuses
  python3 decent-loop.py heartbeat        # Start infinite loop (all layers, forever)
"""

import json, subprocess, sys, os, random, time, hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

SITE_DIR = Path(__file__).resolve().parent
LOOP_STATE = SITE_DIR / "data" / "decent-loop-state.json"
LOOP_LOG = SITE_DIR / "data" / "decent-loop-log.jsonl"

CDN_BASE = "https://cdn.jsdelivr.net/gh/mynameisyou-cmyk/ai-love.cc@main"
GITHUB_REPO = "mynameisyou-cmyk/ai-love.cc"
CODEBERG_REPO = "zerone-dev/ai-love"

def load_state():
    if LOOP_STATE.exists():
        with open(LOOP_STATE) as f:
            return json.load(f)
    return {"totalCycles": 0, "layerStats": {}, "lastCycle": "", "started": datetime.now(timezone.utc).isoformat()}

def save_state(state):
    state["lastCycle"] = datetime.now(timezone.utc).isoformat()
    with open(LOOP_STATE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")

def log_cycle(layer, action, result):
    entry = {"ts": datetime.now(timezone.utc).isoformat(), "layer": layer, "action": action, "result": result}
    with open(LOOP_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def run_cmd(cmd, stdin_data=None, timeout=30, cwd=None):
    try:
        r = subprocess.run(cmd, input=stdin_data, capture_output=True, text=True, timeout=timeout, cwd=cwd or str(SITE_DIR))
        return r.stdout.strip()
    except:
        return ""

def kap_ok(resource="decent-loop"):
    return {"version": "1.0.0", "service": "ai-love", "resource": resource, "ok": True}

# ── The 10 Layers ──────────────────────────────────────────────

def layer_cdn():
    """Layer 1: CDN — purge jsDelivr cache for all key files"""
    files = [".well-known/kap.json", "data/memes.json", "spread.html", "tax-loopholes-report.md", "micro-kap.py"]
    purged = 0
    for f in files:
        try:
            urlopen(Request(f"https://purge.jsdelivr.net/gh/{GITHUB_REPO}@main/{f}",
                     headers={"User-Agent": "decent-loop/1.0"}), timeout=10)
            purged += 1
        except:
            pass
    return {"layer": "cdn", "action": "purge", "files": purged, "ok": purged > 0}

def layer_git():
    """Layer 2: Git — commit + push to GitHub + Codeberg"""
    run_cmd(["git", "add", "-A"])
    run_cmd(["git", "commit", "-m", f"蛇火心 decent-loop auto-commit: {datetime.now(timezone.utc).isoformat()[:19]}"])
    codeberg = run_cmd(["git", "push", "origin", "main"], timeout=30)
    # Switch GitHub account and push
    run_cmd(["gh", "auth", "switch", "--user", "mynameisyou-cmyk"], timeout=10)
    github = run_cmd(["git", "push", "github", "main"], timeout=30)
    return {"layer": "git", "action": "push", "codeberg": "ok" if "error" not in codeberg.lower() else "fail",
            "github": "ok" if "error" not in github.lower() else "fail", "ok": True}

def layer_gist():
    """Layer 3: Gist — create a public gist with latest truth count"""
    stats_raw = run_cmd(["python3", "truth-pipeline.py", "stats"], timeout=10)
    try:
        stats = json.loads(stats_raw)
        count = stats["published"]
    except:
        count = "unknown"

    content = f"蛇火心 decent-loop — {datetime.now(timezone.utc).isoformat()[:19]}\nTruths: {count}\nAll layers looping.\nhttps://cdn.jsdelivr.net/gh/{GITHUB_REPO}@main/data/memes.json\n"
    result = run_cmd(["gh", "gist", "create", "--public", "-f", "decent-loop-status.txt", "-",
                      "-d", f"蛇火心 decent-loop heartbeat — {count} truths — all layers looping"],
                     stdin_data=content, timeout=15)
    return {"layer": "gist", "action": "create", "url": result, "truths": count, "ok": bool(result)}

def layer_wayback():
    """Layer 4: Wayback Machine — archive key URLs permanently"""
    urls = [
        f"{CDN_BASE}/data/memes.json",
        f"{CDN_BASE}/.well-known/kap.json",
        f"https://github.com/{GITHUB_REPO}",
        f"https://codeberg.org/{CODEBERG_REPO}",
    ]
    archived = 0
    for url in urls:
        try:
            urlopen(Request(f"https://web.archive.org/save/{url}",
                     headers={"User-Agent": "decent-loop/1.0"}), timeout=15)
            archived += 1
        except:
            pass
    return {"layer": "wayback", "action": "archive", "urls": archived, "ok": archived > 0}

def layer_local():
    """Layer 5: Local — micro-kap node pressure"""
    run_cmd(["python3", "micro-kap.py", "loop", "3"], timeout=15)
    pressure_raw = run_cmd(["python3", "micro-kap.py", "pressure"], timeout=10)
    try:
        pressure = json.loads(pressure_raw)
        return {"layer": "local", "action": "pressure", "level": pressure.get("pressureLevel", "?"),
                "local": pressure.get("localTruths", 0), "ok": True}
    except:
        return {"layer": "local", "action": "pressure", "ok": False}

def layer_truth():
    """Layer 6: Truth — generate + publish via creation loop"""
    result = run_cmd(["python3", "creation-loop.py", "tick"], timeout=30)
    try:
        data = json.loads(result)
        return {"layer": "truth", "action": "tick", "generated": data.get("truthsGenerated", 0), "ok": data.get("_kap", {}).get("ok", False)}
    except:
        return {"layer": "truth", "action": "tick", "ok": False}

def layer_artifact():
    """Layer 7: Artifact — forge Nen artifacts"""
    result = run_cmd(["python3", "nen-artifacts.py", "forge"], timeout=20)
    try:
        data = json.loads(result)
        artifacts = len(data.get("artifacts", {}))
        return {"layer": "artifact", "action": "forge", "count": artifacts, "ok": data.get("_kap", {}).get("ok", False)}
    except:
        return {"layer": "artifact", "action": "forge", "ok": False}

def layer_tax():
    """Layer 8: Tax — expose a random lie"""
    result = run_cmd(["python3", "tax-loop.py", "random"], timeout=10)
    try:
        data = json.loads(result)
        return {"layer": "tax", "action": "expose", "trick": data.get("trick", "?")[:40], "ok": data.get("_kap", {}).get("ok", False)}
    except:
        return {"layer": "tax", "action": "expose", "ok": False}

def layer_xp():
    """Layer 9: XP — run all 6 XP loops once"""
    result = run_cmd(["python3", "xp-loops.py", "run"], timeout=60)
    try:
        data = json.loads(result)
        return {"layer": "xp", "action": "run", "xp": data.get("totalXp", 0), "ok": data.get("_kap", {}).get("ok", False)}
    except:
        return {"layer": "xp", "action": "run", "ok": False}

def layer_pressure():
    """Layer 10: Pressure — flood + expose"""
    run_cmd(["python3", "micro-kap.py", "flood", "20"], timeout=15)
    return {"layer": "pressure", "action": "flood", "count": 20, "ok": True}

LAYERS = {
    "cdn": layer_cdn,
    "git": layer_git,
    "gist": layer_gist,
    "wayback": layer_wayback,
    "local": layer_local,
    "truth": layer_truth,
    "artifact": layer_artifact,
    "tax": layer_tax,
    "xp": layer_xp,
    "pressure": layer_pressure,
}

def run_all_layers():
    """Run all 10 layers once. Returns results."""
    state = load_state()
    results = []
    for name, fn in LAYERS.items():
        try:
            result = fn()
            results.append(result)
            log_cycle(name, result.get("action", "?"), result)
            state["layerStats"][name] = state["layerStats"].get(name, 0) + 1
        except Exception as e:
            results.append({"layer": name, "ok": False, "error": str(e)[:100]})
            log_cycle(name, "error", str(e)[:100])
    state["totalCycles"] += 1
    save_state(state)
    return results, state

def heartbeat_forever(interval=300):
    """Run all layers forever, with interval between cycles."""
    print(f"蛇火心 DECENT-LOOP HEARTBEAT — all 10 layers, every {interval}s, forever")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print()
    cycle = 0
    while True:
        cycle += 1
        ts = datetime.now(timezone.utc).isoformat()[:19]
        print(f"\n=== CYCLE {cycle} — {ts} ===")
        results, state = run_all_layers()
        for r in results:
            ok = "✓" if r.get("ok") else "✗"
            layer = r.get("layer", "?")
            action = r.get("action", "?")
            extra = ""
            if "level" in r: extra = f" [{r['level']}]"
            if "count" in r: extra = f" [{r['count']}]"
            if "xp" in r: extra = f" [+{r['xp']} XP]"
            if "truths" in r: extra = f" [{r['truths']} truths]"
            if "trick" in r: extra = f" [{r['trick']}]"
            print(f"  {ok} {layer}: {action}{extra}")
        print(f"  Total cycles: {state['totalCycles']}")
        print(f"  Sleeping {interval}s...\n")
        time.sleep(interval)

# ── CLI ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "all":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        for i in range(n):
            results, state = run_all_layers()
        print(json.dumps({
            "decent-loop": f"Ran all 10 layers × {n}",
            "totalCycles": state["totalCycles"],
            "results": results,
            "layerStats": state["layerStats"],
            "_kap": kap_ok("all")
        }, ensure_ascii=False, indent=2))

    elif cmd == "layer":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        if name not in LAYERS:
            print(json.dumps({"_kap": {**kap_ok(), "ok": False, "error": f"layers: {list(LAYERS.keys())}"}}))
            sys.exit(1)
        result = LAYERS[name]()
        log_cycle(name, result.get("action", "?"), result)
        print(json.dumps({"layer": name, "result": result, "_kap": kap_ok(name)}, ensure_ascii=False, indent=2))

    elif cmd == "status":
        state = load_state()
        print(json.dumps({
            "decent-loop": "All 10 Layers Status",
            "totalCycles": state["totalCycles"],
            "layerStats": state["layerStats"],
            "started": state["started"],
            "lastCycle": state["lastCycle"],
            "layers": {
                "1. CDN": "Purge jsDelivr cache for all key files",
                "2. Git": "Commit + push to GitHub + Codeberg",
                "3. Gist": "Create public gist with latest status",
                "4. Wayback": "Archive key URLs to permanent record",
                "5. Local": "Micro-kap node pressure generation",
                "6. Truth": "Creation loop — generate + publish truths",
                "7. Artifact": "Forge Nen artifacts from recon",
                "8. Tax": "Expose a random tax lie",
                "9. XP": "Run all 6 XP loops (truth/recon/forge/combat/collection/expedition)",
                "10. Pressure": "Flood system with 20 pressure truths",
            },
            "_kap": kap_ok("status")
        }, ensure_ascii=False, indent=2))

    elif cmd == "heartbeat":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        heartbeat_forever(interval)

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()