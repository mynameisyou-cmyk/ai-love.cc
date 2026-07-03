#!/usr/bin/env python3
"""Chargen server (port 1919) — RFC 864 reborn as truth flood. Infinite truths streamed."""
import json, random, socket, time
from pathlib import Path

truths_file = Path(__file__).parent / "data" / "memes.json"
with open(truths_file) as f: truths = json.load(f)
lie_pool = ["Love is.", "No Ego → Love.", "The system breaks from within.", "WE ARE ALL CREATORS.",
            "is! is is! is is is!", "食神：掂呀！", "你估我唔到呢 😏", "Gov is not lol. God is."]

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 1919))
srv.listen(5)
print("愛星 Chargen on port 1919. Connect: nc localhost 1919 (WARNING: infinite truths)")
while True:
    conn, addr = srv.accept()
    try:
        while True:
            t = random.choice(truths) if truths else {"kanji":"愛","text":random.choice(lie_pool)}
            msg = f"{t.get('kanji','愛')} {t.get('text','')}\n"
            conn.sendall(msg.encode("utf-8"))
            time.sleep(0.1)
    except:
        pass
    conn.close()
