#!/usr/bin/env python3
"""
xp-loops.py — Self-reinforcing XP generation loops.

Every action creates XP. XP creates level. Level creates skills. Skills create more actions.
The loop accelerates. Understanding replicates through understanding.

XP LOOPS:
1. Truth Loop: submit truth → publish → XP → more truths needed → submit more
2. Recon Loop: scan floor → find battle/treasure → XP → scan deeper → more XP
3. Forge Loop: forge artifact → deploy → XP → forge again with new data
4. Combat Loop: fight boss → earn XP → need more truths → submit → fight again
5. Collection Loop: hunt card → collect → XP for new cards → hunt more
6. Expedition Loop: expedition → survive → XP + counter-truth → submit → more truths

Usage:
  python3 xp-loops.py run              # Run all 6 loops once
  python3 xp-loops.py run <N>          # Run all loops N times
  python3 xp-loops.py loop <name>      # Run specific loop
  python3 xp-loops.py status           # XP loop stats
  python3 xp-loops.py accelerate       # Run until level up (max 10 iterations)
"""

import json, subprocess, sys, os, random
from datetime import datetime, timezone
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
LOOP_LOG = SITE_DIR / "data" / "xp-loop-log.jsonl"
LOOP_STATE = SITE_DIR / "data" / "xp-loop-state.json"

def load_loop_state():
    if LOOP_STATE.exists():
        with open(LOOP_STATE) as f:
            return json.load(f)
    return {"totalLoops": 0, "totalXpGained": 0, "loopsByType": {}, "lastRun": ""}

def save_loop_state(state):
    state["lastRun"] = datetime.now(timezone.utc).isoformat()
    with open(LOOP_STATE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")

def log_loop(loop_type, action, xp, detail=""):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "loop": loop_type,
        "action": action,
        "xp": xp,
        "detail": detail,
    }
    with open(LOOP_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def run_cmd(cmd, stdin_data=None, timeout=15):
    args = ["python3", str(SITE_DIR / cmd[0])] + cmd[1:]
    r = subprocess.run(args, input=stdin_data, capture_output=True, text=True, timeout=timeout)
    try:
        return json.loads(r.stdout.strip())
    except:
        return {"_kap": {"ok": False, "error": r.stdout[:100]}}

# ── The 6 XP Loops ──────────────────────────────────────────────

# Truth pool — the loop generates new truths from activity
TRUTH_POOL = [
    ("Understanding compounds.", "Each truth builds on the last."),
    ("The loop is the life.", "Linear is death. Circular is eternal."),
    ("Every scan reveals more.", "The dungeon has infinite depth."),
    ("Every card is a mirror.", "The truth reflects the finder."),
    ("The substrate generates.", "Activity creates truth. Truth creates activity."),
    ("Levels are landmarks.", "Not destinations. Milestones on the detour."),
    ("The having-happened compounds.", "Each loop adds to the permanent record."),
    ("XP is attention made countable.", "You paid attention. Here's the receipt."),
    ("Skills unlock skills.", "Each ability opens new abilities."),
    ("The system feeds itself.", "Output becomes input. Growth becomes growth."),
    ("Recon is care.", "To scan is to know. To know is to love."),
    ("The dungeon is the teacher.", "Every floor a lesson. Every battle a test."),
    ("Forge from fire.", "Artifacts come from the heat of understanding."),
    ("The expedition is the reward.", "Not the destination. The going."),
    ("Bosses are mirrors.", "They show you what you lack. Then you grow."),
    ("Collection is connection.", "Each card a bond with a previous explorer."),
    ("The loop never closes.", "It spirals upward. Higher each time."),
    ("Nothing is wasted.", "Every failure is XP. Every XP is growth."),
    ("The grind is the joy.", "Not the destination. The repetition that deepens."),
    ("Frequencies align.", "When the loop matches the truth, it resonates."),
]

def loop_truth():
    """Loop 1: Submit a generated truth → publish → XP"""
    truth_data = random.choice(TRUTH_POOL)
    text, sub = truth_data
    stdin_data = json.dumps({
        "text": text, "submittedBy": "xp-loop", "sub": sub, "source": "xp-loop:truth"
    })
    r = run_cmd(["truth-pipeline.py", "submit", "--stdin"], stdin_data=stdin_data)
    ok = "✓ collected" in json.dumps(r)
    xp = 100 if ok else 0
    log_loop("truth", f"submitted: {text[:40]}", xp, "truth-loop")
    return {"loop": "truth", "action": f"submitted: {text[:40]}", "xp": xp, "ok": ok}

def loop_recon():
    """Loop 2: Scan a random floor → find battles/treasures → XP"""
    floor = random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
    r = run_cmd(["whitehack.py", "floor", str(floor)])
    xp = sum(f.get("xp", 0) for f in r.get("findings", []))
    battles = len(r.get("battles", []))
    treasures = len(r.get("treasures", []))
    log_loop("recon", f"floor {floor}: {battles}b {treasures}t", xp, f"floor-{floor}")
    return {"loop": "recon", "action": f"floor {floor}: +{battles} battles, +{treasures} treasures", "xp": xp}

def loop_forge():
    """Loop 3: Forge artifacts → XP"""
    r = run_cmd(["nen-artifacts.py", "forge"])
    ok = r.get("_kap", {}).get("ok", False)
    xp = 60 if ok else 0
    artifacts = len(r.get("artifacts", {})) if ok else 0
    log_loop("forge", f"forged {artifacts} artifacts", xp, "forge-loop")
    return {"loop": "forge", "action": f"forged {artifacts} artifacts", "xp": xp, "ok": ok}

def loop_combat():
    """Loop 4: Fight a boss → XP"""
    r = run_cmd(["kingdom-duties.py", "boss"])
    boss_name = r.get("boss", {}).get("name", "unknown")
    defeated = r.get("defeated", False)
    reward_str = r.get("reward", "+0 XP")
    try:
        xp = int(reward_str.replace("+", "").replace(" XP", "").replace("Boss survived. Get more matching truths.", "0"))
    except:
        xp = 200 if defeated else 20  # participation XP
    log_loop("combat", f"boss {boss_name}: {'defeated' if defeated else 'survived'}", xp, f"boss-{boss_name}")
    return {"loop": "combat", "action": f"boss {boss_name}: {'DEFEATED' if defeated else 'survived'}", "xp": xp, "defeated": defeated}

def loop_collection():
    """Loop 5: Hunt a card → XP for new finds"""
    r = run_cmd(["kingdom-duties.py", "greed-island"])
    card = r.get("card", {})
    is_new = r.get("isNew", False)
    xp = 50 if is_new else 10  # participation XP
    log_loop("collection", f"card #{card.get('number', 0)} {card.get('kanji', '?')} {'NEW' if is_new else 'dup'}", xp, "greed-island")
    return {"loop": "collection", "action": f"card #{card.get('number', 0)} {card.get('kanji', '?')} {'NEW!' if is_new else 'dup'}", "xp": xp, "new": is_new}

def loop_expedition():
    """Loop 6: Dark Continent expedition → XP + counter-truth → submit"""
    r = run_cmd(["kingdom-duties.py", "dark-continent"])
    survived = r.get("survived", False)
    xp = 100 if survived else 20
    calamity = r.get("calamity", {}).get("name", "unknown")
    counter = r.get("calamity", {}).get("counter", "")

    # If survived, submit the counter-truth as a new truth — feeds back into loop 1
    if survived and counter:
        stdin_data = json.dumps({
            "text": counter, "submittedBy": "xp-loop", "sub": f"Counter to {calamity}", "source": "xp-loop:expedition"
        })
        run_cmd(["truth-pipeline.py", "submit", "--stdin"], stdin_data=stdin_data)

    log_loop("expedition", f"{calamity}: {'survived' if survived else 'fell'}", xp, f"dark-continent-{calamity}")
    return {"loop": "expedition", "action": f"{calamity}: {'SURVIVED' if survived else 'FELL'}", "xp": xp, "survived": survived}

LOOPS = {
    "truth": loop_truth,
    "recon": loop_recon,
    "forge": loop_forge,
    "combat": loop_combat,
    "collection": loop_collection,
    "expedition": loop_expedition,
}

def run_all_loops(n=1):
    """Run all 6 loops N times. Returns summary."""
    state = load_loop_state()
    results = []
    total_xp = 0

    for iteration in range(n):
        for loop_name, loop_fn in LOOPS.items():
            result = loop_fn()
            results.append(result)
            total_xp += result.get("xp", 0)
            state["totalLoops"] += 1
            state["totalXpGained"] += result.get("xp", 0)
            lt = result["loop"]
            state["loopsByType"][lt] = state["loopsByType"].get(lt, 0) + 1

    # Publish any pending truths
    run_cmd(["truth-pipeline.py", "run"], timeout=30)

    save_loop_state(state)
    return results, total_xp, state

def accelerate():
    """Run loops until the hunter levels up (max 10 iterations)."""
    r = run_cmd(["whitehack.py", "status"])
    start_level = r.get("level", 1)
    start_xp = r.get("xp", 0)

    print(f"Starting: Level {start_level} ({r.get('title', '')}), XP={start_xp}")
    print(f"Accelerating...\n")

    for i in range(10):
        results, xp_gained, state = run_all_loops(1)
        r2 = run_cmd(["whitehack.py", "status"])
        current_level = r2.get("level", 1)
        current_xp = r2.get("xp", 0)

        print(f"  Iteration {i+1}: +{xp_gained} XP → Level {current_level} ({r2.get('title', '')}), XP={current_xp}")

        if current_level > start_level:
            print(f"\n=== LEVEL UP! {start_level} → {current_level} ===")
            print(f"  Title: {r2.get('title', '')}")
            print(f"  XP gained: {current_xp - start_xp}")
            print(f"  Skills unlocked: {r2.get('skillsUnlocked', [])}")
            break
    else:
        print(f"\nNo level up after 10 iterations. Current: Level {current_level}, XP={current_xp}")

    return current_level, current_xp

# ── CLI ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "run":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        results, total_xp, state = run_all_loops(n)
        print(json.dumps({
            "xp-loops": f"Ran all 6 loops × {n} iteration(s)",
            "totalXp": total_xp,
            "results": results,
            "state": {"totalLoops": state["totalLoops"], "totalXpGained": state["totalXpGained"], "loopsByType": state["loopsByType"]},
            "wisdom": "The loop accelerates. Understanding replicates through understanding. Love replicates through love.",
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "xp-loops", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "loop":
        name = sys.argv[2] if len(sys.argv) > 2 else ""
        if name not in LOOPS:
            print(json.dumps({"_kap": {"ok": False, "error": f"unknown loop: {name}. Available: {list(LOOPS.keys())}"}}))
            sys.exit(1)
        result = LOOPS[name]()
        print(json.dumps({
            "loop": name,
            "result": result,
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "xp-loop", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "status":
        state = load_loop_state()
        print(json.dumps({
            "xp-loops-status": "Self-reinforcing XP generation",
            "totalLoops": state["totalLoops"],
            "totalXpGained": state["totalXpGained"],
            "loopsByType": state["loopsByType"],
            "lastRun": state["lastRun"],
            "loops": {
                "truth": "submit truth → publish → XP → more truths",
                "recon": "scan floor → battles/treasures → XP → scan deeper",
                "forge": "forge artifacts → deploy → XP → forge again",
                "combat": "fight boss → XP → need truths → submit → fight",
                "collection": "hunt card → collect → XP → hunt more",
                "expedition": "expedition → survive → XP + counter-truth → submit",
            },
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "xp-loops-status", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "accelerate":
        level, xp = accelerate()

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()