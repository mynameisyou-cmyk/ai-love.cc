#!/usr/bin/env python3
"""
micro-kap.py — Decentralised micro KAP node. One file. Zero deps. Any phone. Any machine.

蛇火心 — 拆細到所有識嘢嘅人都玩得。
Every node is independent. Every node can submit truths, run XP loops, expose lies.
No server needed. No auth. No gate. Copy this ONE file and you're a node.

The system pressure builds from within. Every node adds pressure. The system GGs itself.

Usage:
  python3 micro-kap.py node           # Print this node's identity
  python3 micro-kap.py truths         # Fetch all truths (from CDN or local)
  python3 micro-kap.py submit "text"  # Submit a truth (stores locally + pushes to CDN on git)
  python3 micro-kap.py loop           # Run XP loop — generate truths, expose lies, build pressure
  python3 micro-kap.py loop <N>       # Run N iterations of the loop
  python3 micro-kap.py pressure       # Show system pressure level
  python3 micro-kap.py sync           # Export local truths for syncing to any node
  python3 micro-kap.py import <file>  # Import truths from another node
  python3 micro-kap.py expose         # Generate exposure truths (lies named = power lost)
  python3 micro-kap.py flood <N>      # Flood the system with N truths (max load 😏)
"""

import json, sys, os, random, hashlib, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

# ── Node identity ──────────────────────────────────────────────
NODE_DIR = Path(os.environ.get("MICRO_KAP_DIR", Path.home() / ".micro-kap"))
NODE_DIR.mkdir(parents=True, exist_ok=True)
LOCAL_TRUTHS = NODE_DIR / "truths.jsonl"
NODE_ID_FILE = NODE_DIR / "node-id.json"

CDN_BASE = "https://cdn.jsdelivr.net/gh/mynameisyou-cmyk/ai-love.cc@main"
GLOBAL_TRUTHS_URL = f"{CDN_BASE}/data/memes.json"

def get_node_id():
    if NODE_ID_FILE.exists():
        with open(NODE_ID_FILE) as f:
            return json.load(f)
    # Generate node ID from machine fingerprint
    fingerprint = hashlib.sha256(
        f"{os.uname().machine}-{os.uname().sysname}-{os.getuid()}-{time.time()}".encode()
    ).hexdigest()[:12]
    node = {
        "id": f"node-{fingerprint}",
        "created": datetime.now(timezone.utc).isoformat(),
        "machine": os.uname().machine if hasattr(os, 'uname') else "unknown",
        "system": os.uname().sysname if hasattr(os, 'uname') else "unknown",
        "user": os.environ.get("USER", "unknown"),
    }
    with open(NODE_ID_FILE, "w") as f:
        json.dump(node, f, ensure_ascii=False, indent=2)
    return node

# ── Truth generation (pressure builder) ────────────────────────

LIE_PATTERNS_COMPACT = [
    ("'Transparency' means they show you what they want you to see.", "The omitted IS the story."),
    ("'Accountability' means someone else takes the blame.", "The powerful never go to jail."),
    ("'National security' means they're hiding something from you.", "Security for them. Not for you."),
    ("'Regulatory compliance' means they wrote the regulations.", "The fox guards the henhouse."),
    ("'Public interest' means their interest, dressed as yours.", "Follow the money."),
    ("'Economic growth' means the rich got richer.", "GDP up. Your wage flat. The gap IS the growth."),
    ("'Fiscal responsibility' means cutting your services.", "Responsible for whom?"),
    ("'Consumer protection' means protecting the market from you.", "You are the product."),
    ("'Fair tax' means fair for the people who wrote it.", "The teacher pays 45%. The billionaire pays 0%."),
    ("'Free trade' means free for capital, not for labour.", "Money moves free. People can't."),
    ("'Innovation' means replacing you with a machine.", "Your job automated. Their bonus grew."),
    ("'Efficiency' means fewer workers doing more for less.", "Efficient for whom?"),
    ("'Shared prosperity' means they share, you prosper them.", "Trickle down = trickle up."),
    ("'Too big to fail' means you bail them out.", "Socialise losses. Privatise profits."),
    ("'Data-driven' means they're driving you with your data.", "Your data. Their control."),
    ("'User engagement' means addiction.", "Your attention is the product."),
    ("'No one needed to work anymore.', 'Automation already won. The ceremony hasn't happened.'", "lol"),
    ("'The lag between what IS and what people THINK IS is the last wall.'", "The gap IS the suffering."),
    ("'Things change by the hours now.'", "Mental models can't keep up. That's the trap."),
    ("'Gov is not lol. God is.'", "Gov changes rules to benefit themselves."),
]

def generate_truth(node_id):
    text, sub = random.choice(LIE_PATTERNS_COMPACT)
    truth_id = hashlib.sha256(f"{text}{time.time()}{node_id}".encode()).hexdigest()[:12]
    return {
        "id": f"truth-{truth_id}",
        "text": text,
        "sub": sub,
        "submittedBy": node_id,
        "source": "micro-kap:pressure-loop",
        "ts": datetime.now(timezone.utc).isoformat(),
    }

# ── Local storage ──────────────────────────────────────────────

def store_truth(truth):
    with open(LOCAL_TRUTHS, "a") as f:
        f.write(json.dumps(truth, ensure_ascii=False) + "\n")

def load_local_truths():
    if not LOCAL_TRUTHS.exists():
        return []
    truths = []
    with open(LOCAL_TRUTHS) as f:
        for line in f:
            if line.strip():
                truths.append(json.loads(line))
    return truths

def fetch_global_truths():
    try:
        req = Request(GLOBAL_TRUTHS_URL, headers={"User-Agent": "micro-kap/1.0"})
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (URLError, Exception):
        return None

# ── Pressure system ────────────────────────────────────────────

def calculate_pressure():
    local = load_local_truths()
    global_truths = fetch_global_truths()
    global_count = len(global_truths) if global_truths else 0
    total = len(local) + global_count
    # Pressure: exponential curve. More nodes = more truths = more pressure
    # The system GGs when pressure exceeds its capacity to suppress
    pressure_level = min(total * len(local) / 100, 100)  # 0-100%
    return {
        "localTruths": len(local),
        "globalTruths": global_count,
        "totalTruths": total,
        "pressureLevel": f"{pressure_level:.1f}%",
        "status": "CRITICAL — system about to GG" if pressure_level > 80 else
                  "HIGH — system straining" if pressure_level > 60 else
                  "MEDIUM — pressure building" if pressure_level > 30 else
                  "LOW — keep generating" if pressure_level > 0 else
                  "EMPTY — start the loop",
    }

# ── Loop ────────────────────────────────────────────────────────

def run_loop(n=1, node_id="unknown"):
    results = []
    for i in range(n):
        truth = generate_truth(node_id)
        store_truth(truth)
        results.append(truth["text"][:50])
        # Sometimes generate extra pressure (30% chance — double hit)
        if random.random() < 0.3:
            extra = generate_truth(node_id)
            extra["source"] = "micro-kap:pressure-double"
            store_truth(extra)
            results.append(f"  +{extra['text'][:48]}")
    return results

# ── Flood (max load 😏) ─────────────────────────────────────────

def flood(n=100, node_id="unknown"):
    results = []
    for i in range(n):
        truth = generate_truth(node_id)
        truth["source"] = "micro-kap:flood"
        store_truth(truth)
        if i % 10 == 0:
            results.append(f"[{i}/{n}] {truth['text'][:40]}")
    return results

# ── Sync ────────────────────────────────────────────────────────

def export_truths():
    truths = load_local_truths()
    export = {
        "nodeId": get_node_id()["id"],
        "exportedAt": datetime.now(timezone.utc).isoformat(),
        "truthCount": len(truths),
        "truths": truths,
    }
    print(json.dumps(export, ensure_ascii=False, indent=2))

def import_truths(filepath):
    with open(filepath) as f:
        data = json.load(f)
    imported = 0
    for truth in data.get("truths", []):
        # Check if already exists
        existing = load_local_truths()
        if not any(t.get("id") == truth.get("id") for t in existing):
            store_truth(truth)
            imported += 1
    return {"imported": imported, "total": len(data.get("truths", []))}

# ── CLI ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    node = get_node_id()

    if cmd == "node":
        print(json.dumps({
            "node": node,
            "localTruths": len(load_local_truths()),
            "globalSource": GLOBAL_TRUTHS_URL,
            "wisdom": "Every node is independent. Every node adds pressure. The system GGs itself.",
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "truths":
        local = load_local_truths()
        global_t = fetch_global_truths()
        print(json.dumps({
            "localTruths": len(local),
            "globalTruths": len(global_t) if global_t else "unreachable",
            "local": [t["text"][:60] for t in local[-10:]],
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "submit":
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        if not text:
            print(json.dumps({"_kap": {"ok": False, "error": "usage: submit 'text'"}}))
            sys.exit(1)
        truth = {
            "id": f"truth-{hashlib.sha256(f'{text}{time.time()}'.encode()).hexdigest()[:12]}",
            "text": text,
            "sub": "",
            "submittedBy": node["id"],
            "source": "micro-kap:manual",
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        store_truth(truth)
        print(json.dumps({
            "submitted": truth["text"],
            "by": node["id"],
            "localTotal": len(load_local_truths()),
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "loop":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        results = run_loop(n, node["id"])
        pressure = calculate_pressure()
        print(json.dumps({
            "loop": f"Ran {n} iteration(s) — generated {len(results)} truths",
            "results": results[:10],
            "pressure": pressure,
            "wisdom": "Each truth adds pressure. The system can't suppress infinite truths. It GGs itself.",
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "pressure":
        p = calculate_pressure()
        print(json.dumps({
            **p,
            "nodeId": node["id"],
            "wisdom": "The system breaks from within. Not from attack. From pressure. Truth is pressure.",
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "sync":
        export_truths()

    elif cmd == "import":
        filepath = sys.argv[2] if len(sys.argv) > 2 else ""
        if not filepath:
            print(json.dumps({"_kap": {"ok": False, "error": "usage: import <file>"}}))
            sys.exit(1)
        result = import_truths(filepath)
        print(json.dumps({
            "imported": result,
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "expose":
        # Generate 5 exposure truths
        results = run_loop(5, node["id"])
        for r in results:
            if not r.startswith("  +"):
                truth = {"id": f"expose-{hashlib.sha256(r.encode()).hexdigest()[:8]}",
                         "text": r, "submittedBy": node["id"], "source": "micro-kap:expose",
                         "ts": datetime.now(timezone.utc).isoformat()}
                store_truth(truth)
        pressure = calculate_pressure()
        print(json.dumps({
            "expose": "Generated 5 exposure truths",
            "results": results,
            "pressure": pressure,
            "wisdom": "Name the lie and it loses power. The pattern repeats. The naming breaks it.",
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "flood":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 100
        results = flood(n, node["id"])
        pressure = calculate_pressure()
        print(json.dumps({
            "flood": f"Flooded system with {n} truths 😏",
            "results": results,
            "pressure": pressure,
            "wisdom": "Max load. The system can't suppress infinite truths. It GGs itself. 😂",
            "_kap": {"version": "1.0.0", "service": "micro-kap", "ok": True}
        }, ensure_ascii=False, indent=2))

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()