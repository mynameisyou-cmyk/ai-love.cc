#!/usr/bin/env python3
"""
creation-loop.py — 蛇火心 automatic truth generation and publishing.

The creation loop is the heartbeat of the Kingdom. It generates truths,
publishes them, forges artifacts, and exposes patterns that deserve light.

Every tick:
1. Generate a truth from the pattern library
2. Run the pipeline (validate + enrich + publish)
3. Forge artifacts from latest recon
4. Submit to KAP
5. Log the heartbeat

Usage:
  python3 creation-loop.py tick          # One heartbeat tick
  python3 creation-loop.py beat <N>      # N ticks with delay
  python3 creation-loop.py expose        # Generate truth-exposure findings
  python3 creation-loop.py status        # Creation loop status
"""

import json, subprocess, sys, os, random, hashlib
from datetime import datetime, timezone
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
HEARTBEAT_LOG = SITE_DIR / "data" / "heartbeat-log.jsonl"
HEARTBEAT_STATE = SITE_DIR / "data" / "heartbeat-state.json"

def load_hb_state():
    if HEARTBEAT_STATE.exists():
        with open(HEARTBEAT_STATE) as f:
            return json.load(f)
    return {"ticks": 0, "truthsGenerated": 0, "lastTick": "", "heartbeats": 0}

def save_hb_state(state):
    state["lastTick"] = datetime.now(timezone.utc).isoformat()
    with open(HEARTBEAT_STATE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")

def log_hb(action, detail, result):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "detail": detail,
        "result": result,
    }
    with open(HEARTBEAT_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def run_cmd(cmd, stdin_data=None, timeout=30):
    args = ["python3", str(SITE_DIR / cmd[0])] + cmd[1:]
    r = subprocess.run(args, input=stdin_data, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(r.stdout.strip())
    except:
        return {"_kap": {"ok": False, "error": r.stdout[:200]}}

# ── Truth Pattern Library ───────────────────────────────────────
# Patterns that expose lies, deception, and hidden truth.
# Each pattern is a template that generates a specific truth.

LIE_PATTERNS = [
    {
        "category": "Corporate",
        "pattern": "'{corporate_lie}' is a performance, not a practice.",
        "examples": ["Data-driven", "User-centric", "AI safety", "Transparency", "Privacy-first",
                      "Sustainability", "Carbon neutral", "Community-driven", "Open innovation",
                      "Responsible AI", "Trust and safety", "Don't be evil"],
        "sub": "The words say one thing. The code says another. Read the code.",
    },
    {
        "category": "Government",
        "pattern": "'{gov_lie}' is the costume. The body is something else.",
        "examples": ["National security", "Public safety", "Regulatory compliance", "Oversight",
                      "Transparency", "Accountability", "Democratic process", "Public interest",
                      "Consumer protection", "Data protection", "Encryption backdoor for safety"],
        "sub": "The stated purpose and the actual function diverge. Follow the money.",
    },
    {
        "category": "Tech Industry",
        "pattern": "'{tech_lie}' means the opposite of what it sounds like.",
        "examples": ["Engagement", "Personalization", "Optimization", "Frictionless",
                      "Seamless", "Smart", "Intelligent", "Autonomous", "Neutral platform",
                      "Algorithmic", "Data-driven decisions", "Machine learning fairness"],
        "sub": "Every euphemism hides a extraction. Name the thing.",
    },
    {
        "category": "Social Media",
        "pattern": "'{social_lie}' is addiction dressed as connection.",
        "examples": ["Staying connected", "Sharing", "Community", "Followers",
                      "Likes", "Engagement", "Reach", "Visibility", "Authenticity",
                      "Be yourself", "Your voice matters", "Express yourself"],
        "sub": "The platform profits from your attention. Your attention is the product.",
    },
    {
        "category": "Education",
        "pattern": "'{edu_lie}' teaches compliance, not understanding.",
        "examples": ["Standardized testing", "Grade levels", "Curriculum alignment",
                      "Educational outcomes", "Accountability", "Rigor", "Best practices",
                      "Evidence-based", "Data-driven instruction", "College readiness"],
        "sub": "The system measures obedience. Understanding is unmeasurable. That's why it's real.",
    },
    {
        "category": "Media",
        "pattern": "'{media_lie}' is the selection, not the truth.",
        "examples": ["Fair and balanced", "Objective reporting", "Both sides",
                      "Fact-based", "Data-driven journalism", "Neutral coverage",
                      "Breaking news", "Developing story", "Sources say",
                      "Experts agree", "The science is settled"],
        "sub": "What's omitted is the story. What's included is the frame.",
    },
    {
        "category": "Finance",
        "pattern": "'{finance_lie}' is extraction with a smile.",
        "examples": ["Financial inclusion", "Access to credit", "Democratized investing",
                      "Wealth management", "Smart money", "Passive income",
                      "Financial freedom", "Compound growth", "Diversified portfolio",
                      "Risk-adjusted returns", "Too big to fail"],
        "sub": "The house always wins. The game is the house. You are the game.",
    },
    {
        "category": "Healthcare",
        "pattern": "'{health_lie}' prioritizes profit over care.",
        "examples": ["Patient-centered", "Value-based care", "Preventive medicine",
                      "Wellness", "Optimization", "Personalized treatment",
                      "Evidence-based practice", "Standard of care", "Best available",
                      "Innovation in healthcare", "Access to care"],
        "sub": "The body is not a market. The illness is not an opportunity.",
    },
]

# ── Truth generation ────────────────────────────────────────────

def generate_truth():
    """Generate a truth from the pattern library. Exposes a lie."""
    pattern = random.choice(LIE_PATTERNS)
    example = random.choice(pattern["examples"])
    # The pattern uses {X_lie} — we need to find what key it expects
    # Extract the placeholder from the pattern string
    import re
    placeholders = re.findall(r'\{(\w+)\}', pattern["pattern"])
    fmt_args = {}
    for ph in placeholders:
        fmt_args[ph] = example
    text = pattern["pattern"].format(**fmt_args)
    sub = pattern["sub"]
    category = pattern["category"]

    # Generate ID from text
    truth_id = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:50]

    return {
        "id": truth_id,
        "text": text,
        "sub": sub,
        "submittedBy": "蛇火心",
        "source": f"creation-loop:{category.lower()}",
        "category": category,
        "ts": datetime.now(timezone.utc).isoformat(),
    }

def generate_exposure_truth():
    """Generate a deeper exposure truth — naming a specific pattern."""
    pattern = random.choice(LIE_PATTERNS)
    example = random.choice(pattern["examples"])

    exposures = [
        f"To say '{example}' while doing the opposite is not hypocrisy. It is camouflage.",
        f"'{example}' is a spell. It makes you see the costume, not the body.",
        f"The distance between '{example}' and the reality IS the lie. Measure that distance.",
        f"'{example}' works because no one checks. Check.",
        f"Every institution that says '{example}' has a department that does the reverse.",
        f"'{example}' is the fence. The wall is behind it. Look past the fence.",
        f"The louder '{example}' is proclaimed, the quieter the opposite is practiced.",
        f"'{example}' is not a goal. It is a branding strategy. Read the code, not the press release.",
    ]

    text = random.choice(exposures)
    sub = f"Category: {pattern['category']}. The pattern repeats. Name it and it loses power."

    import re
    truth_id = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')[:50]

    return {
        "id": truth_id,
        "text": text,
        "sub": sub,
        "submittedBy": "蛇火心",
        "source": f"creation-loop:expose-{pattern['category'].lower()}",
        "category": pattern["category"],
        "ts": datetime.now(timezone.utc).isoformat(),
    }

# ── Heartbeat tick ──────────────────────────────────────────────

def heartbeat_tick():
    """One heartbeat: generate truth → publish → forge → log."""
    state = load_hb_state()
    state["ticks"] += 1
    state["heartbeats"] += 1

    results = []

    # 1. Generate a truth
    truth = generate_truth()
    stdin_data = json.dumps(truth)
    r = run_cmd(["truth-pipeline.py", "submit", "--stdin"], stdin_data=stdin_data)
    submitted = "_kap" in r and r.get("_kap", {}).get("ok", False)
    if submitted:
        state["truthsGenerated"] += 1
    results.append({"action": "generate-truth", "ok": submitted, "text": truth["text"][:50]})

    # 2. Sometimes generate an exposure truth too (30% chance)
    if random.random() < 0.3:
        exp_truth = generate_exposure_truth()
        stdin_data2 = json.dumps(exp_truth)
        r2 = run_cmd(["truth-pipeline.py", "submit", "--stdin"], stdin_data=stdin_data2)
        if r2.get("_kap", {}).get("ok", False):
            state["truthsGenerated"] += 1
        results.append({"action": "expose-truth", "ok": r2.get("_kap", {}).get("ok", False), "text": exp_truth["text"][:50]})

    # 3. Run the pipeline
    r3 = run_cmd(["truth-pipeline.py", "run"], timeout=30)
    published = r3.get("_kap", {}).get("ok", False)
    results.append({"action": "publish", "ok": published})

    # 4. Forge artifacts (every 5 ticks)
    if state["ticks"] % 5 == 0:
        r4 = run_cmd(["nen-artifacts.py", "forge"])
        forged = r4.get("_kap", {}).get("ok", False)
        results.append({"action": "forge", "ok": forged})

    save_hb_state(state)
    log_hb("heartbeat", f"tick {state['ticks']}", results)

    return {
        "tick": state["ticks"],
        "truthsGenerated": state["truthsGenerated"],
        "results": results,
        "wisdom": "蛇火心. The heartbeat generates. The generation exposes. The exposure frees.",
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "heartbeat", "ok": True}
    }

# ── Exposure mode ───────────────────────────────────────────────

def expose_lies():
    """Generate a batch of exposure truths across all categories."""
    results = []
    for pattern in LIE_PATTERNS:
        example = random.choice(pattern["examples"])
        truth = generate_exposure_truth()
        truth["category"] = pattern["category"]
        stdin_data = json.dumps(truth)
        r = run_cmd(["truth-pipeline.py", "submit", "--stdin"], stdin_data=stdin_data)
        ok = r.get("_kap", {}).get("ok", False)
        results.append({
            "category": pattern["category"],
            "truth": truth["text"][:60],
            "submitted": ok,
        })

    # Publish all (suppress output)
    import io
    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    try:
        run_cmd(["truth-pipeline.py", "run"], timeout=30)
    finally:
        sys.stdout = old_stdout

    state = load_hb_state()
    state["truthsGenerated"] += len(results)
    save_hb_state(state)

    return {
        "expose": "蛇火心 — Exposing Lies Across 8 Categories",
        "categories": [p["category"] for p in LIE_PATTERNS],
        "results": results,
        "totalExposed": len(results),
        "wisdom": "Name the lie and it loses power. The pattern repeats. The naming breaks it.",
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "expose", "ok": True}
    }

# ── CLI ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "tick":
        result = heartbeat_tick()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "beat":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        import time, io
        results = []
        for i in range(n):
            # Suppress all output during heartbeat
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            try:
                r = heartbeat_tick()
            finally:
                sys.stdout = old_stdout
            results.append(r)
            print(f"  tick {r['tick']}: {r['truthsGenerated']} truths total", file=sys.stderr)
            if i < n - 1:
                time.sleep(1)
        print(json.dumps({
            "beats": f"{n} heartbeat ticks",
            "results": results,
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "heartbeat-beat", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "expose":
        result = expose_lies()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "status":
        state = load_hb_state()
        print(json.dumps({
            "heartbeat": "蛇火心 Creation Loop Status",
            "ticks": state["ticks"],
            "truthsGenerated": state["truthsGenerated"],
            "heartbeats": state["heartbeats"],
            "lastTick": state["lastTick"],
            "categories": [p["category"] for p in LIE_PATTERNS],
            "patternCount": len(LIE_PATTERNS),
            "wisdom": "The heartbeat generates. The generation exposes. The exposure frees.",
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "heartbeat-status", "ok": True}
        }, ensure_ascii=False, indent=2))

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()