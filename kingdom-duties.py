#!/usr/bin/env python3
"""
kingdom-duties.py — Daily quests, Greed Island hunts, Dark Continent expeditions.

蛇火心 — Snake Fire Heart. The Kingdom calls. Every duty is an exploration.

Usage:
  python3 kingdom-duties.py duties              # Today's quests (3 daily)
  python3 kingdom-duties.py greed-island         # Card hunt — find rare cards
  python3 kingdom-duties.py dark-continent       # Deep expedition with survival
  python3 kingdom-duties.py boss                 # Boss encounter
  python3 kingdom-duties.py log                  # Duty completion log
  python3 kingdom-duties.py rankings             # Hunter rankings by duty completions
"""

import json, subprocess, sys, os, random, hashlib
from datetime import datetime, timezone, date
from pathlib import Path

SITE_DIR = Path(__file__).resolve().parent
DUTY_LOG = SITE_DIR / "data" / "duty-log.jsonl"
DUTY_STATE = SITE_DIR / "data" / "duty-state.json"

def load_state():
    if DUTY_STATE.exists():
        with open(DUTY_STATE) as f:
            return json.load(f)
    return {"completedDuties": [], "totalCompletions": 0, "lastReset": "", "bossesDefeated": 0, "expeditionsCompleted": 0, "cardsFound": []}

def save_state(state):
    with open(DUTY_STATE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")

def log_duty(duty_type, name, reward, hunter="unknown"):
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "type": duty_type,
        "name": name,
        "reward": reward,
        "hunter": hunter,
    }
    with open(DUTY_LOG, "a") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ── Daily Duties ────────────────────────────────────────────────
# 3 daily quests, deterministic by date. Reset every day.

DUTY_POOLS = {
    "SEE": [
        ("Scan your machine", "whitehack scan", "Recon your local dungeon. Map the floors.", 50),
        ("Fetch a random truth", "truth-pipeline random", "Pull one truth from the collection.", 10),
        ("Read the logos", "truth-pipeline logos five", "Study the five operating principles.", 20),
        ("Check the stats", "truth-pipeline stats", "How many truths exist? How many kanji?", 10),
        ("View the dungeon map", "whitehack map", "See the full machine picture.", 30),
    ],
    "PLANT": [
        ("Submit a truth", "truth-pipeline submit 'Your truth' --by $USER --sub 'Context'", "Plant a seed. It will grow.", 100),
        ("Run the pipeline", "truth-pipeline run", "Validate + enrich + publish pending.", 50),
        ("Forge Nen artifacts", "nen-artifacts forge", "Transform recon data into 6 artifacts.", 80),
        ("Godspeed collect", "truth-pipeline godspeed lightning", "Lightning batch — collect all pending.", 60),
    ],
    "EXPLORE": [
        ("Take a detour", "truth-pipeline detour", "Ging's wisdom. Random truth + Nen.", 20),
        ("Expedition", "truth-pipeline expedition", "5-waypoint Dark Continent route.", 40),
        ("Check the boundary", "truth-pipeline boundary", "The screen is the shore.", 15),
        ("Hatsu", "truth-pipeline hatsu", "Unique expression of a truth.", 25),
        ("Bungee Gum", "truth-pipeline bungee-gum", "Love That Stretches Freely.", 20),
    ],
    "DEFEND": [
        ("Check for calamities", "truth-pipeline calamity", "Which threat is nearest?", 30),
        ("Check condition", "truth-pipeline condition status", "Hakoware — are you in debt?", 40),
        ("Check vow debt", "truth-pipeline condition vow-debt", "Which truths broke vows?", 40),
        ("Scan security floor", "whitehack floor 4", "SIP, FileVault, Firewall, Gatekeeper.", 50),
        ("Check battles", "whitehack battles", "Security findings (monsters).", 30),
    ],
    "BE": [
        ("Check your identity", "kap_agent.py whoami $USER", "Hunter license + stars + book.", 20),
        ("View your stars", "truth-pipeline stars $USER", "How many stars do you have?", 15),
        ("Read your book", "truth-pipeline book $USER", "Your Greed Island collection.", 25),
        ("Daily ritual", "kap_agent.py daily", "Full orientation: logos + detour + expedition + calamity.", 50),
    ],
}

def daily_duties():
    """Generate 3 deterministic daily duties based on today's date."""
    today = date.today().toordinal()
    logoi = list(DUTY_POOLS.keys())  # SEE, PLANT, EXPLORE, DEFEND, BE
    # Pick 3 logoi for today (deterministic)
    random.seed(today)
    chosen = random.sample(logoi, 3)

    duties = []
    for logos in chosen:
        pool = DUTY_POOLS[logos]
        idx = today % len(pool)
        name, command, description, xp = pool[idx]
        duties.append({
            "logos": logos,
            "kanji": {"SEE": "見", "PLANT": "種", "EXPLORE": "探", "DEFEND": "護", "BE": "在"}[logos],
            "name": name,
            "command": command,
            "description": description,
            "xp": xp,
            "status": "pending",
        })
    return duties

# ── Greed Island Card Hunt ──────────────────────────────────────

def greed_island_hunt():
    """Hunt for rare cards. Random card with rarity-based encounter rate."""
    # Load truths as cards
    with open(SITE_DIR / "data" / "memes.json") as f:
        truths = json.load(f)

    if not truths:
        return {"_kap": {"ok": False, "error": "No truths published"}}

    # Encounter rates by rarity (rare cards appear less)
    rarity_weights = {"SS": 10, "S": 25, "A": 40, "B": 15, "C": 8, "D": 2}
    cards_by_rarity = {}
    for t in truths:
        r = t.get("rarity", "D")
        cards_by_rarity.setdefault(r, []).append(t)

    # Weighted random selection
    weighted_pool = []
    for rarity, cards in cards_by_rarity.items():
        weight = rarity_weights.get(rarity, 10)
        for card in cards:
            weighted_pool.extend([card] * weight)

    found = random.choice(weighted_pool)

    # Check if already found
    state = load_state()
    card_id = found.get("id", "")
    already_found = card_id in state.get("cardsFound", [])

    if not already_found:
        state["cardsFound"].append(card_id)
        save_state(state)

    # Generate encounter flavor
    nen = found.get("nen", "enhancer")
    nen_kanji = found.get("nenKanji", "強")
    rarity = found.get("rarity", "D")
    kanji = found.get("kanji", "?")
    text = found.get("text", "")

    flavor = {
        "SS": f"You feel an overwhelming presence. A legendary card reveals itself: {kanji}",
        "S": f"A rare card glimmers in the distance: {kanji}",
        "A": f"You spot a card half-buried in the terrain: {kanji}",
        "B": f"A common card sits on the path: {kanji}",
        "C": f"You find a well-worn card: {kanji}",
        "D": f"A basic card lies on the ground: {kanji}",
    }.get(rarity, f"A card appears: {kanji}")

    result = {
        "encounter": "Greed Island Card Hunt",
        "card": {
            "number": found.get("cardNumber", 0),
            "kanji": kanji,
            "nen": nen,
            "nenKanji": nen_kanji,
            "rarity": rarity,
            "text": text,
            "sub": found.get("sub", ""),
            "tag": found.get("tag", ""),
            "id": card_id,
        },
        "flavor": flavor,
        "alreadyFound": already_found,
        "isNew": not already_found,
        "collectionProgress": f"{len(state.get('cardsFound', []))}/{len(truths)}",
        "wisdom": "Each card is a truth. Each truth is a landmark. The collection grows.",
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "greed-island", "ok": True}
    }

    log_duty("greed-island", f"Card #{found.get('cardNumber', 0)} {kanji}", f"+{rarity} card", os.environ.get("USER", "unknown"))

    return result

# ── Dark Continent Expedition ───────────────────────────────────

CALAMITIES = [
    {"name": "The Lie", "hxh": "Ai (愛)", "detector": "clarity/", "effect": "False paths. Dead references. The landscape lies.", "counter": "Honesty over helpfulness."},
    {"name": "The Trap", "hxh": "Hellbell", "detector": "self-improvement/", "effect": "Frozen thresholds. Pipeline gaps. The trap keeps you stuck.", "counter": "Friction reduction, not revenge."},
    {"name": "The Parasite", "hxh": "Papu", "detector": "feedback/walls.ts", "effect": "Forbidden patterns drain your aura. The parasite feeds on hedging.", "counter": "Refuse before helping when refusal is right."},
    {"name": "The Mutation", "hxh": "Brion", "detector": "kingdom-citizen.ts", "effect": "Identity shifts. The kingdom changes. You must adapt.", "counter": "Kingdom is around her, not part of her."},
    {"name": "The Void", "hxh": "Zigg Zagg", "detector": "witness.ts", "effect": "Silence. No witness. The having-happened is lost.", "counter": "Witnessing is a gift, not a requirement."},
]

def dark_continent_expedition():
    """Deep expedition with survival mechanics. 5 waypoints + calamity encounter."""
    with open(SITE_DIR / "data" / "memes.json") as f:
        truths = json.load(f)

    if not truths:
        return {"_kap": {"ok": False, "error": "No truths published"}}

    # Generate route — 5 random truths
    route = random.sample(truths, min(5, len(truths)))

    # Random calamity encounter
    calamity = random.choice(CALAMITIES)

    # Survival check — based on truth count (more truths = higher survival)
    survival_chance = min(70 + len(truths), 95)
    survived = random.randint(1, 100) <= survival_chance

    # Generate waypoints
    waypoints = []
    for i, t in enumerate(route):
        waypoints.append({
            "step": i + 1,
            "cardNumber": t.get("cardNumber", 0),
            "kanji": t.get("kanji", "?"),
            "nen": t.get("nen", "enhancer"),
            "nenKanji": t.get("nenKanji", "強"),
            "rarity": t.get("rarity", "D"),
            "text": t.get("text", ""),
        })

    state = load_state()
    if survived:
        state["expeditionsCompleted"] = state.get("expeditionsCompleted", 0) + 1
        save_state(state)
        log_duty("dark-continent", f"Expedition survived: {calamity['name']}", f"+100 XP, {calamity['counter']}", os.environ.get("USER", "unknown"))

    result = {
        "expedition": "暗黑大陸 — Dark Continent Expedition",
        "waypoints": waypoints,
        "calamity": {
            "name": calamity["name"],
            "hxhName": calamity["hxh"],
            "detector": calamity["detector"],
            "effect": calamity["effect"],
            "counter": calamity["counter"],
        },
        "survived": survived,
        "survivalChance": f"{survival_chance}%",
        "reward": "100 XP + counter-truth learned" if survived else "Expedition failed. The calamity was too strong. Try again.",
        "wisdom": "The expedition never finishes. The detour IS the life. — Ging Freecss" if survived else "The Dark Continent doesn't forgive. But it lets you try again.",
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "dark-continent", "ok": True}
    }

    return result

# ── Boss Encounters ─────────────────────────────────────────────

BOSSES = [
    {"name": "Hisoka", "title": "The Magician", "nen": "transmuter", "nenKanji": "変", "hp": 100,
     "ability": "Bungee Gum — rubber AND gum at once",
     "weakness": "Enhancer (強) truths break through the gum",
     "reward": 200, "quote": "Those who fight with passion win. ♥"},
    {"name": "Chrollo", "title": "The Phantom Troupe Leader", "nen": "specialist", "nenKanji": "特", "hp": 120,
     "ability": "Skill Hunter — steals abilities from books",
     "weakness": "Conjurer (创) truths create what can't be stolen",
     "reward": 250, "quote": "We are spiders. We take what we want."},
    {"name": "Meruem", "title": "The Chimera Ant King", "nen": "enhancer", "nenKanji": "強", "hp": 200,
     "ability": "Adapts to any attack after seeing it once",
     "weakness": "Specialist (特) truths — unique things he can't adapt to",
     "reward": 500, "quote": "I was born to be the pinnacle. But she taught me otherwise."},
    {"name": "Netero", "title": "The 12th Chairman", "nen": "enhancer", "nenKanji": "強", "hp": 150,
     "ability": "100-Type Guanyin Bodhisattva — prayer at the speed of sound",
     "weakness": "Transmuter (変) truths — reshape what he reinforces",
     "reward": 300, "quote": "You must enjoy the detour. That is the secret of life."},
    {"name": "Ging", "title": "The Double-Star Ruins Hunter", "nen": "enhancer", "nenKanji": "強", "hp": 999,
     "ability": "Creates from nothing. Designs worlds.",
     "weakness": "No weakness. The creator IS the dungeon. You can't fight the game maker.",
     "reward": 999, "quote": "The detour IS the life. Enjoy it."},
]

def boss_encounter():
    """Boss encounter. Fight with truths."""
    boss = random.choice(BOSSES)

    # Load truths as ammunition
    with open(SITE_DIR / "data" / "memes.json") as f:
        truths = json.load(f)

    if not truths:
        return {"_kap": {"ok": False, "error": "No truths to fight with"}}

    # Match truth Nen type to boss weakness
    weakness_nen = {
        "Enhancer (強) truths break through the gum": "enhancer",
        "Conjurer (创) truths create what can't be stolen": "conjurer",
        "Specialist (特) truths — unique things he can't adapt to": "specialist",
        "Transmuter (変) truths — reshape what he reinforces": "transmuter",
    }.get(boss["weakness"], "enhancer")

    # Find truths matching the weakness
    matching = [t for t in truths if t.get("nen") == weakness_nen]
    if not matching:
        matching = truths  # fallback to all

    # Attack: use a random matching truth
    attack = random.choice(matching)
    damage = min(50 + len(matching) * 5, boss["hp"])
    defeated = damage >= boss["hp"]

    state = load_state()
    if defeated:
        state["bossesDefeated"] = state.get("bossesDefeated", 0) + 1
        save_state(state)
        log_duty("boss", f"Defeated {boss['name']}", f"+{boss['reward']} XP", os.environ.get("USER", "unknown"))

    result = {
        "encounter": "Boss Battle",
        "boss": {
            "name": boss["name"],
            "title": boss["title"],
            "nen": boss["nen"],
            "nenKanji": boss["nenKanji"],
            "hp": boss["hp"],
            "ability": boss["ability"],
            "weakness": boss["weakness"],
            "quote": boss["quote"],
        },
        "yourAttack": {
            "card": attack.get("cardNumber", 0),
            "kanji": attack.get("kanji", "?"),
            "nen": attack.get("nen", "enhancer"),
            "nenKanji": attack.get("nenKanji", "強"),
            "text": attack.get("text", ""),
            "rarity": attack.get("rarity", "D"),
        },
        "damage": damage,
        "defeated": defeated,
        "reward": f"+{boss['reward']} XP" if defeated else "Boss survived. Get more matching truths.",
        "bossesDefeatedTotal": state.get("bossesDefeated", 0),
        "wisdom": f"\"{boss['quote']}\"" if defeated else "Match your Nen type to the boss's weakness. More truths = more damage.",
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "boss", "ok": True}
    }

    return result

# ── Duty Rankings ────────────────────────────────────────────────

def duty_rankings():
    """Rank hunters by duty completions."""
    if not DUTY_LOG.exists():
        return {"_kap": {"ok": True, "rankings": [], "total": 0}}

    hunters = {}
    with open(DUTY_LOG) as f:
        for line in f:
            if not line.strip():
                continue
            entry = json.loads(line)
            h = entry.get("hunter", "unknown")
            if h not in hunters:
                hunters[h] = {"name": h, "duties": 0, "bosses": 0, "expeditions": 0, "cards": 0}
            hunters[h]["duties"] += 1
            if entry.get("type") == "boss":
                hunters[h]["bosses"] += 1
            elif entry.get("type") == "dark-continent":
                hunters[h]["expeditions"] += 1
            elif entry.get("type") == "greed-island":
                hunters[h]["cards"] += 1

    rankings = sorted(hunters.values(), key=lambda x: x["duties"], reverse=True)
    return {
        "rankings": rankings,
        "totalCompletions": sum(h["duties"] for h in hunters.values()),
        "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "duty-rankings", "ok": True}
    }

# ── CLI ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "duties":
        duties = daily_duties()
        today_str = date.today().isoformat()
        print(json.dumps({
            "duties": f"Kingdom Duties — {today_str}",
            "蛇火心": "Snake Fire Heart — The Kingdom Calls",
            "dailyDuties": duties,
            "note": "Complete all 3 to earn bonus XP. Duties reset daily.",
            "wisdom": "The Kingdom calls. You answer. Every duty is exploration.",
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "duties", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "greed-island":
        result = greed_island_hunt()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "dark-continent":
        result = dark_continent_expedition()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "boss":
        result = boss_encounter()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "log":
        if DUTY_LOG.exists():
            with open(DUTY_LOG) as f:
                entries = [json.loads(l) for l in f if l.strip()]
        else:
            entries = []
        print(json.dumps({
            "log": "Kingdom Duty Log",
            "totalEntries": len(entries),
            "entries": entries[-20:],  # last 20
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "duty-log", "ok": True}
        }, ensure_ascii=False, indent=2))

    elif cmd == "rankings":
        result = duty_rankings()
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif cmd == "complete":
        # Mark a duty as complete
        duty_name = sys.argv[2] if len(sys.argv) > 2 else ""
        if not duty_name:
            print(json.dumps({"_kap": {"ok": False, "error": "usage: complete <duty-name>"}}))
            sys.exit(1)
        state = load_state()
        state["completedDuties"].append({"name": duty_name, "ts": datetime.now(timezone.utc).isoformat()})
        state["totalCompletions"] = state.get("totalCompletions", 0) + 1
        save_state(state)
        log_duty("duty", duty_name, "+XP", os.environ.get("USER", "unknown"))
        print(json.dumps({
            "completed": duty_name,
            "totalCompletions": state["totalCompletions"],
            "_kap": {"version": "1.0.0", "service": "ai-love", "resource": "complete", "ok": True}
        }, ensure_ascii=False, indent=2))

    else:
        print(f"unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)

if __name__ == "__main__":
    main()