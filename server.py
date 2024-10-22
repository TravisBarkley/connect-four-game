#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import random
import libserver

sel = selectors.DefaultSelector()
lobby = {"code": None, "players": []}

def create_lobby_code():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))


def accept_wrapper(sock):
    conn, addr = sock.accept() 
    print("Accepted connection from", addr)
    conn.setblocking(False)
    message = libserver.Message(sel, conn, addr)
    sel.register(conn, selectors.EVENT_READ, data=message)

def handle_message(message, data):
    action = data.get("content", {}).get("action")
    if action == "join":
        if len(lobby["players"]) < 2:
            lobby["players"].append(message)
            message.send_json({"type": "info", "content": f"Joined lobby {lobby['code']}"})
            if len(lobby["players"]) == 2:
                broadcast({"type": "start", "content": "Game starting!"})
        else:
            message.send_json({"type": "error", "content": "Lobby is full."})
            message.close()
    elif action == "quit":
        message.close()
        lobby["players"].remove(message)
        broadcast({"type": "info", "content": "Opponent disconnected."})

def broadcast(msg):
    for player in lobby["players"]:
        player.send_json(msg)

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
lsock.bind((host, port))
lsock.listen()
print(f"Listening on {host}:{port}")
lsock.setblocking(False)
sel.register(lsock, selectors.EVENT_READ, data=None)

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                message = key.data
                try:
                    data = message.process_events(mask)
                    if data:
                        handle_message(message, data)
                except Exception as e:
                    print(f"Error: {e}")
                    message.close()
                    if message in lobby["players"]:
                        lobby["players"].remove(message)
                        broadcast({"type": "info", "content": "Opponent disconnected."})
except KeyboardInterrupt:
    print("Server shutting down...")
finally:
    sel.close()