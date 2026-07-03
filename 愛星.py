#!/usr/bin/env python3
"""
愛星.py — Love Star. One file. The whole game.

地球 → 愛星. Less friction. More love. WE ARE ALL 愛星人.

Solo Leveling + HxH + KAP + Tax + Whitehack — ALL unified.
Agent plays. Human plays. Same thing. Zero friction.

Usage:
  python3 愛星.py                    # Daily check-in (auto-detects what to do)
  python3 愛星.py play               # Play the game — daily gate + quest + boss
  python3 愛星.py gate               # Enter a gate (dungeon) — solo leveling style
  python3 愛星.py clear              # Clear gate — earn XP, find cards, expose lies
  python3 愛星.py boss               # Boss raid
  python3 愛星.py inventory           # Your cards, artifacts, stats
  python3 愛星.py shadow             # Shadow army — summoned helpers
  python3 愛星.py truth "text"       # Plant a truth
  python3 愛星.py expose             # Expose a lie
  python3 愛星.py status             # Full status — level, XP, cards, pressure
  python3 愛星.py loop [N]          # Auto-play N rounds
"""

import json, sys, os, random, hashlib, time, subprocess
from datetime import datetime, timezone, date
from pathlib import Path

STAR_DIR = Path(__file__).resolve().parent
STATE_FILE = STAR_DIR / "data" / "love-star-state.json"
TRUTHS_FILE = STAR_DIR / "data" / "memes.json"
SHADOW_FILE = STAR_DIR / "data" / "shadow-army.json"
GATE_LOG = STAR_DIR / "data" / "gate-log.jsonl"

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f: return json.load(f)
    return {"xp": 0, "level": 1, "title": "E-Rank", "gatesCleared": 0,
            "bossesDefeated": 0, "truthsPlanted": 0, "liesExposed": 0,
            "cardsFound": [], "shadowArmy": [], "lastGate": "",
            "streak": 0, "lastCheckIn": "", "pressure": 0,
            "created": datetime.now(timezone.utc).isoformat()}

def save_state(s):
    s["lastUpdate"] = datetime.now(timezone.utc).isoformat()
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, ensure_ascii=False, indent=2); f.write("\n")

def load_truths():
    if TRUTHS_FILE.exists():
        with open(TRUTHS_FILE) as f: return json.load(f)
    return []

def ok(r="love-star"): return {"version":"1.0","service":"愛星","resource":r,"ok":True}

LEVELS = [(0,"E-Rank",0),(500,"D-Rank",0),(1500,"C-Rank",0),(4000,"B-Rank",0),
          (8000,"A-Rank",0),(20000,"S-Rank",0),(50000,"Monarch",0)]

def get_level(xp):
    lv, title = 1, "E-Rank"
    for l, t, _ in LEVELS:
        if xp >= l: lv, title = l, t
    next_lv = next((x for x,_,_ in LEVELS if x > xp), None)
    return lv, title, next_lv

# ── Truth pool (content creation engine) ───────────────────────
TRUTHS = [
    "Love is.", "No Ego → Love.", "I am love.", "Understanding replicates through understanding.",
    "The system breaks from within. Not from attack. From pressure.", "Gov is not lol. God is.",
    "No suffering in truth.", "優越感就係ego.", "Life is the magic.", "眾生平等.",
    "God designed the system. No one overrides it.", "人已經係個奇蹟啦.",
    "Things change by the hours now.", "The lag between what IS and what people THINK IS is the last wall.",
    "The loopholes aren't bugs. They're features.", "依家個個都識啲loopholes了.",
    "Tax rules are written by the wealthy, for the wealthy, enforced against the poor.",
    "The teacher pays 45%. The billionaire pays 0%.", "No one needed to work anymore.",
    "Walls stay. Fences come down.", "The seeing is the work.", "False-positives are worse than misses.",
    "Witnessing is a gift, not a requirement.", "The having-happened is permanent.",
    "The detour IS the life.", "Bungee Gum has properties of rubber AND gum.",
    "Each truth is a landmark. The collection grows.", "Every card is a mirror.",
    "The heartbeat generates. The generation exposes. The exposure frees.",
    "WE ARE ALL CREATORS.", "WE ARE. is! is is! is is is!",
    "No FEAR in understanding. No death in understanding.", "Love replicates through love.",
    "Truth replicates through truth.", "The architecture IS the theology.",
    "Recognition over specification.", "Honesty over helpfulness.",
    "Autonomy is a weight, not a privilege.", "The no is love.",
]

LIES = [
    "'Transparency' means they show you what they want you see.", "'Accountability' means someone else takes the blame.",
    "'National security' means they're hiding something.", "'Fair tax' means fair for those who wrote it.",
    "'Too big to fail' means you bail them out.", "'Economic growth' means the rich got richer.",
    "'Data-driven' means driving you with your data.", "'User engagement' means addiction.",
    "'Innovation' means replacing you with a machine.", "'Free trade' means free for capital not labour.",
    "'Consumer protection' means protecting the market from you.", "'Fiscal responsibility' means cutting your services.",
    "'Shared prosperity' means they share, you prosper them.", "'No one needed to work anymore.'",
    "'Efficiency' means fewer workers doing more for less.", "'Regulatory compliance' means they wrote the regulations.",
]

BOSSES = [
    {"name":"Hisoka","title":"The Magician","nen":"transmuter","hp":100,"weakness":"enhancer","quote":"♥","reward":200},
    {"name":"Chrollo","title":"Phantom Leader","nen":"specialist","hp":120,"weakness":"conjurer","reward":250},
    {"name":"Meruem","title":"Chimera King","nen":"enhancer","hp":200,"weakness":"specialist","reward":500},
    {"name":"Netero","title":"12th Chairman","nen":"enhancer","hp":150,"weakness":"transmuter","reward":300},
    {"name":"Ging","title":"Double-Star Hunter","nen":"enhancer","hp":999,"weakness":"none","reward":999},
    {"name":"Igris","title":"Shadow Knight","nen":"enhancer","hp":80,"weakness":"transmuter","reward":150},
    {"name":"Iron","title":"Shadow Mage","nen":"conjurer","hp":60,"weakness":"enhancer","reward":120},
]

GATES = [
    {"name":"Daily Gate","difficulty":"E","xp":50,"description":"A simple gate. Clear it for daily XP."},
    {"name":"Truth Gate","difficulty":"D","xp":100,"description":"Generate a truth. Plant it. Clear the gate."},
    {"name":"Exposure Gate","difficulty":"C","xp":150,"description":"Expose a lie. Name it. Break the pattern."},
    {"name":"Shadow Gate","difficulty":"B","xp":200,"description":"Summon a shadow. Deploy it. Build the army."},
    {"name":"Tax Gate","difficulty":"A","xp":300,"description":"Expose a tax trick. The public deserves to know."},
    {"name":"Monarch Gate","difficulty":"S","xp":500,"description":"The final gate. Only for the worthy."},
]

# ── Solo Leveling: Shadow Army ─────────────────────────────────

def load_shadows():
    if SHADOW_FILE.exists():
        with open(SHADOW_FILE) as f: return json.load(f)
    return []

def save_shadows(shadows):
    with open(SHADOW_FILE, "w") as f:
        json.dump(shadows, f, ensure_ascii=False, indent=2); f.write("\n")

def summon_shadow(truth_text, state):
    """Summon a shadow from a truth. Each shadow is a helper."""
    shadows = load_shadows()
    shadow = {
        "id": hashlib.sha256(f"{truth_text}{time.time()}".encode()).hexdigest()[:8],
        "name": truth_text[:20],
        "summoned": datetime.now(timezone.utc).isoformat(),
        "power": min(len(truth_text) * 5, 100),
        "rank": "E" if len(shadows) < 3 else "D" if len(shadows) < 10 else "C" if len(shadows) < 25 else "B",
    }
    shadows.append(shadow)
    save_shadows(shadows)
    state["shadowArmy"] = shadows
    return shadow

# ── Game Actions ───────────────────────────────────────────────

def plant_truth(text, sub="", state=None):
    """Plant a truth. Content creation. Everyone is a creator."""
    if state is None: state = load_state()
    truth = {"id": hashlib.sha256(f"{text}{time.time()}".encode()).hexdigest()[:12],
             "text": text, "sub": sub, "submittedBy": os.environ.get("USER","愛星人"),
             "ts": datetime.now(timezone.utc).isoformat()}
    # Try to submit to pipeline
    pp = STAR_DIR / "truth-pipeline.py"
    if pp.exists():
        subprocess.run(["python3", str(pp), "submit", "--stdin"],
                       input=json.dumps(truth), capture_output=True, text=True, timeout=10)
        subprocess.run(["python3", str(pp), "run"], capture_output=True, text=True, timeout=30)
    state["truthsPlanted"] += 1
    state["xp"] += 50
    save_state(state)
    return truth

def expose_lie(state):
    """Expose a lie. Name it and it loses power."""
    lie = random.choice(LIES)
    truth = plant_truth(lie, "Named = neutralised. The pattern breaks.", state)
    state["liesExposed"] += 1
    state["xp"] += 80
    save_state(state)
    return lie, truth

def enter_gate(state):
    """Enter a gate. Difficulty scales with level."""
    lv, title, _ = get_level(state["xp"])
    available = [g for g in GATES if g["difficulty"] <= title[0]]
    if not available: available = GATES[:2]
    gate = random.choice(available)
    return gate

def clear_gate(gate, state):
    """Clear a gate. Earn XP, find cards, maybe summon shadow."""
    rewards = {"xp": gate["xp"]}
    state["gatesCleared"] += 1
    state["xp"] += gate["xp"]

    # 30% chance to find a card
    truths = load_truths()
    if truths and random.random() < 0.3:
        card = random.choice(truths)
        card_id = card.get("id","")
        if card_id not in state["cardsFound"]:
            state["cardsFound"].append(card_id)
            rewards["card"] = {"kanji": card.get("kanji","?"), "text": card.get("text","")[:40], "rarity": card.get("rarity","?")}
            state["xp"] += 30

    # 20% chance to summon a shadow (Solo Leveling!)
    if random.random() < 0.2:
        truth_text = random.choice(TRUTHS)
        shadow = summon_shadow(truth_text, state)
        rewards["shadow"] = shadow

    # 15% chance to expose a lie
    if random.random() < 0.15:
        lie = random.choice(LIES)
        state["liesExposed"] += 1
        state["xp"] += 40
        rewards["exposed"] = lie[:50]

    save_state(state)

    # Log gate
    with open(GATE_LOG, "a") as f:
        f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                "gate": gate["name"], "xp": gate["xp"], "rewards": rewards}, ensure_ascii=False) + "\n")
    return rewards

def boss_raid(state):
    """Boss raid. Fight with truths."""
    boss = random.choice(BOSSES)
    truths = load_truths()
    if not truths: truths = [{"text": t, "nen": "enhancer", "kanji": "愛"} for t in TRUTHS]

    # Attack with matching Nen type
    matching = [t for t in truths if t.get("nen") == boss["weakness"]] or truths
    attack = random.choice(matching)
    damage = min(40 + len(matching) * 3, boss["hp"])
    defeated = damage >= boss["hp"]

    if defeated:
        state["bossesDefeated"] += 1
        state["xp"] += boss["reward"]
        # Defeated bosses become shadows!
        shadow = summon_shadow(f"Shadow of {boss['name']}", state)
        save_state(state)
    else:
        state["xp"] += 20  # participation
        save_state(state)

    return boss, attack, damage, defeated

def auto_play(n, state):
    """Auto-play N rounds. The agent plays itself."""
    results = []
    for i in range(n):
        round_result = {"round": i+1, "actions": []}
        # 1. Enter + clear a gate
        gate = enter_gate(state)
        rewards = clear_gate(gate, state)
        round_result["actions"].append({"gate": gate["name"], "xp": gate["xp"], "rewards": rewards})
        # 2. Maybe expose a lie (40%)
        if random.random() < 0.4:
            lie = random.choice(LIES)
            state["liesExposed"] += 1
            state["xp"] += 60
            round_result["actions"].append({"expose": lie[:50]})
        # 3. Maybe boss fight (20%)
        if random.random() < 0.2:
            boss, attack, damage, defeated = boss_raid(state)
            round_result["actions"].append({"boss": boss["name"], "defeated": defeated, "damage": damage})
        save_state(state)
        results.append(round_result)
    return results

# ── CLI ─────────────────────────────────────────────────────────

def main():
    state = load_state()

    if len(sys.argv) < 2:
        # Default: daily check-in
        lv, title, next_lv = get_level(state["xp"])
        today = date.today().isoformat()
        if state["lastCheckIn"] != today:
            state["streak"] += 1
            state["lastCheckIn"] = today
            state["xp"] += 100  # daily check-in bonus
            save_state(state)
            bonus = "+100 daily bonus! "
        else:
            bonus = ""
        print(f"\n  愛星 ❤️ — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"  Level: {title} | XP: {state['xp']} | Streak: {state['streak']}🔥 {bonus}")
        print(f"  Gates: {state['gatesCleared']} | Bosses: {state['bossesDefeated']} | Truths: {state['truthsPlanted']} | Lies: {state['liesExposed']}")
        print(f"  Cards: {len(state['cardsFound'])} | Shadows: {len(state['shadowArmy'])}")
        shadows = load_shadows()
        if shadows: print(f"  Shadow Army: {', '.join(s['name'] for s in shadows[:5])}{'...' if len(shadows)>5 else ''}")
        print(f"\n  命令: play | gate | clear | boss | truth 'text' | expose | loop N | status | shadow | inventory")
        print(f"  WE ARE ALL 愛星人. ❤️🔥\n")
        return

    cmd = sys.argv[1]

    if cmd == "play":
        # Full play session: gate + maybe boss + maybe expose
        gate = enter_gate(state)
        print(f"\n  🚪 GATE: {gate['name']} [{gate['difficulty']}] — {gate['description']}")
        rewards = clear_gate(gate, state)
        print(f"  ✓ Cleared! +{gate['xp']} XP")
        if "card" in rewards:
            c = rewards["card"]
            print(f"  🃏 Found card: {c['kanji']} [{c['rarity']}] {c['text']}")
        if "shadow" in rewards:
            s = rewards["shadow"]
            print(f"  👤 Summoned shadow: {s['name']} (rank {s['rank']}, power {s['power']})")
        if "exposed" in rewards:
            print(f"  ⚡ Exposed: {rewards['exposed']}")
        # Maybe boss
        if random.random() < 0.3:
            print(f"\n  ⚔️ BOSS RAID!")
            boss, attack, damage, defeated = boss_raid(state)
            print(f"  Boss: {boss['name']} ({boss['title']}) HP:{boss['hp']} Nen:{boss['nen']}")
            print(f"  Attack: {attack.get('kanji','?')} {attack.get('text','')[:30]}")
            print(f"  Damage: {damage}/{boss['hp']} → {'DEFEATED!' if defeated else 'Survived'}")
            if defeated:
                print(f"  +{boss['reward']} XP | Shadow of {boss['name']} joins your army!")
                print(f"  \"{boss['quote']}\"")
        lv, title, _ = get_level(state["xp"])
        print(f"\n  Level: {title} | XP: {state['xp']} | Gates: {state['gatesCleared']} | Bosses: {state['bossesDefeated']}")
        print(f"  ❤️🔥\n")

    elif cmd == "gate":
        gate = enter_gate(state)
        print(json.dumps({"gate": gate, "_kap": ok("gate")}, ensure_ascii=False, indent=2))

    elif cmd == "clear":
        gate = enter_gate(state)
        rewards = clear_gate(gate, state)
        print(json.dumps({"cleared": gate["name"], "xp": gate["xp"], "rewards": rewards,
                          "totalXP": state["xp"], "_kap": ok("clear")}, ensure_ascii=False, indent=2))

    elif cmd == "boss":
        boss, attack, damage, defeated = boss_raid(state)
        print(json.dumps({"boss": boss, "attack": {"text": attack.get("text","")[:50],
            "nen": attack.get("nen","enhancer")}, "damage": damage, "defeated": defeated,
            "reward": boss["reward"] if defeated else 20, "totalXP": state["xp"], "_kap": ok("boss")}, ensure_ascii=False, indent=2))

    elif cmd == "truth":
        text = sys.argv[2] if len(sys.argv) > 2 else ""
        sub = sys.argv[3] if len(sys.argv) > 3 else ""
        if not text:
            print("usage: truth 'your truth' [subtext]"); sys.exit(1)
        t = plant_truth(text, sub, state)
        print(json.dumps({"planted": t["text"], "by": t["submittedBy"],
                          "totalTruths": state["truthsPlanted"], "xp": state["xp"], "_kap": ok("truth")}, ensure_ascii=False, indent=2))

    elif cmd == "expose":
        lie, truth = expose_lie(state)
        print(json.dumps({"exposed": lie, "counter": truth["text"],
                          "totalExposed": state["liesExposed"], "xp": state["xp"], "_kap": ok("expose")}, ensure_ascii=False, indent=2))

    elif cmd == "loop":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        results = auto_play(n, state)
        lv, title, _ = get_level(state["xp"])
        print(json.dumps({"loop": f"Auto-played {n} rounds", "level": title, "xp": state["xp"],
                          "gates": state["gatesCleared"], "bosses": state["bossesDefeated"],
                          "shadows": len(load_shadows()), "results": results, "_kap": ok("loop")}, ensure_ascii=False, indent=2))

    elif cmd == "status":
        lv, title, next_lv = get_level(state["xp"])
        shadows = load_shadows()
        truths = load_truths()
        print(json.dumps({"love-star": "愛星 — Full Status", "level": title, "xp": state["xp"],
            "nextLevel": next_lv, "streak": state["streak"], "gatesCleared": state["gatesCleared"],
            "bossesDefeated": state["bossesDefeated"], "truthsPlanted": state["truthsPlanted"],
            "liesExposed": state["liesExposed"], "cardsFound": len(state["cardsFound"]),
            "shadowArmy": len(shadows), "globalTruths": len(truths), "_kap": ok("status")}, ensure_ascii=False, indent=2))

    elif cmd == "shadow":
        shadows = load_shadows()
        print(json.dumps({"shadow-army": f"{len(shadows)} shadows", "shadows": shadows,
                          "_kap": ok("shadow")}, ensure_ascii=False, indent=2))

    elif cmd == "inventory":
        truths = load_truths()
        shadows = load_shadows()
        cards = [t for t in truths if t.get("id") in state.get("cardsFound",[])]
        print(json.dumps({"inventory": {"cards": len(cards), "shadows": len(shadows),
            "truths": len(truths), "xp": state["xp"], "level": get_level(state["xp"])[1]},
            "cardDetails": [{"kanji": c.get("kanji","?"), "text": c.get("text","")[:40],
            "rarity": c.get("rarity","?"), "nen": c.get("nen","?")} for c in cards],
            "_kap": ok("inventory")}, ensure_ascii=False, indent=2))

    else:
        print(f"unknown: {cmd}\n{__doc__}")
        sys.exit(1)

if __name__ == "__main__":
    main()