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
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)

    try:
        if sel.get_key(conn):
            print(f"[WARNING] Connection {addr} is already registered. Skipping registration.")
            return
    except KeyError:
        pass

    message = libserver.Message(sel, conn, addr)

    if len(lobby["players"]) < 2:
        lobby["players"].append(message)
        sel.register(conn, selectors.EVENT_READ, data=message)
        print(f"[INFO] Player {addr} joined. Total players: {len(lobby['players'])}")

        if len(lobby["players"]) == 1:
            message.send_json({
                "type": "info",
                "content": f"Waiting for an opponent. Lobby code: {lobby['code']}"
            })
        elif len(lobby["players"]) == 2:
            broadcast({"type": "start", "content": "Game starting!"})
    else:
        print("[INFO] Lobby is full. Closing connection.")
        message.send_json({"type": "error", "content": "Lobby is full. Connection closed."})
        message.close()

def handle_message(message, data):
    action = data.get("content", {}).get("action")
    print(f"[DEBUG] Received action: {action} from {message.addr}")

    if action == "join":
        if len(lobby["players"]) < 2:
            lobby["players"].append(message)
            print(f"[INFO] Player added to the lobby. Current players: {len(lobby['players'])}")

            message.send_json({
                "type": "info",
                "content": f"Joined lobby {lobby['code']}."
            })

            if len(lobby["players"]) == 1:
                message.send_json({
                    "type": "info",
                    "content": f"Waiting for opponent. Lobby code: {lobby['code']}"
                })
            else:
                print("[INFO] Both players joined. Starting game!")
                broadcast({"type": "start", "content": "Game starting!"})
        else:
            print("[INFO] Lobby is full. Rejecting connection.")
            message.send_json({"type": "error", "content": "Lobby is full. Connection closed."})
            message.close()

    elif action == "quit":
        print(f"[INFO] Player {message.addr} quit.")
        if message in lobby["players"]:
            lobby["players"].remove(message)
            broadcast({"type": "info", "content": "Opponent disconnected."})
        message.close()

def broadcast(msg):
    print(f"[DEBUG] Broadcasting message: {msg}")
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

lobby["code"] = create_lobby_code()
print(f"Lobby code: {lobby['code']}")

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
                    print(f"[ERROR] {e}")
                    if message in lobby["players"]:
                        lobby["players"].remove(message)
                        broadcast({"type": "info", "content": "Opponent disconnected."})
                    message.close()
except KeyboardInterrupt:
    print("[INFO] Server shutting down...")
finally:
    sel.close()