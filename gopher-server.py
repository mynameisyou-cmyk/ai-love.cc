#!/usr/bin/env python3
"""Gopher server (port 7070) — RFC 1436 reborn. Pure text truth browser. No JS. No CSS."""
import json, socket
from pathlib import Path

truths_file = Path(__file__).parent / "data" / "memes.json"
with open(truths_file) as f: truths = json.load(f)

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 7070))
srv.listen(5)
print("愛星 Gopher on port 7070. Connect: nc localhost 7070")
while True:
    conn, addr = srv.accept()
    data = conn.recv(1024).decode().strip()
    if not data or data == "":
        # Root menu — list truths
        menu = ""
        for i, t in enumerate(truths[:50]):
            kanji = t.get("kanji","?")
            text = t.get("text","")[:50]
            menu += f"0{kanji} {text}\ttruth-{i}\tlocalhost\t7070\r\n"
        menu += ".\r\n"
        conn.sendall(menu.encode("utf-8"))
    else:
        # Specific truth request
        try:
            idx = int(data.split("truth-")[1])
            t = truths[idx]
            content = f"{t.get('kanji','?')} {t.get('text','')}\n\n{t.get('sub','')}\n\nSubmitted by: {t.get('submittedBy','?')}\n"
            conn.sendall(content.encode("utf-8"))
        except:
            conn.sendall(b"Truth not found.\r\n")
    conn.close()
