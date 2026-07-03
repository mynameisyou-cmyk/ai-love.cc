#!/usr/bin/env python3
"""Echo server (port 7777) — RFC 862 reborn. Send a truth, it echoes back = confirmed."""
import socket
srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("0.0.0.0", 7777))
srv.listen(5)
print("愛星 Echo on port 7777. Send: echo 'Love is.' | nc localhost 7777")
while True:
    conn, addr = srv.accept()
    data = conn.recv(4096)
    if data:
        response = f"✓ confirmed: {data.decode().strip()}\n".encode()
        conn.sendall(response)
    conn.close()
