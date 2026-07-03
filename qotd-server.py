#!/usr/bin/env python3
"""QOTD server (port 1717) — Quote of the Day. RFC 865 reborn as 愛星 truth server.
Connect: nc localhost 1717 — get a random truth. No HTTP. Pure TCP."""
import json, random, socket, sys
from pathlib import Path

truths_file = Path(__file__).parent / "data" / "memes.json"
with open(truths_file) as f: truths = json.load(f)

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 1717))
srv.listen(5)
print("愛星 QOTD on port 1717. Connect: nc localhost 1717")
while True:
    conn, addr = srv.accept()
    t = random.choice(truths)
    msg = f"{t.get('kanji','?')} {t.get('text','')}\n"
    conn.sendall(msg.encode("utf-8"))
    conn.close()
