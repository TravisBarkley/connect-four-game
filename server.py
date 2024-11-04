#!/usr/bin/env python3

import time
import socket
import sys
import threading
import random
import string

host, port = sys.argv[1], int(sys.argv[2])
HEADER = 64
ADDR = (host, port)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

active_connections_lock = threading.Lock()
active_connections = 0
lobbies = {}

def generate_game_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))


def send_message(conn, message):
    message = message.encode("utf-8")
    msg_length = len(message)
    
    # Prepare a HEADER-length length header
    send_length = f"{msg_length:<{HEADER}}".encode("utf-8")
    payload = send_length + message  # Concatenate length header and message

    conn.sendall(payload)  # Send the whole payload in one go

def handle_client(conn, addr):
    global active_connections
    print(f"New Client Connected: {addr}.")

    connected = True
    lobby_code = None
    while connected:
        msg_length = conn.recv(HEADER).decode("utf-8").strip()
        if msg_length:
            try:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode("utf-8")
                print(f"[{addr}] {msg}")

                if msg.startswith("CREATE_LOBBY"):
                    lobby_code = generate_game_code()
                    lobbies[lobby_code] = []
                    send_message(conn, f"LOBBY_CREATED {lobby_code}")
                    print(f"Lobby {lobby_code} created by {addr}")

                elif msg.startswith("JOIN_LOBBY"):
                    lobby_code = msg.split()[1]
                    if lobby_code in lobbies and len(lobbies[lobby_code]) < 2:
                        lobbies[lobby_code].append(conn)
                        player_number = len(lobbies[lobby_code])
                        send_message(conn, f"JOINED_LOBBY {lobby_code}")
                        send_message(conn, f"You are Player {player_number}")
                        print(f"{addr} joined lobby {lobby_code} as Player {player_number}")
                        for client in lobbies[lobby_code]:
                            if client != conn:
                                send_message(client, f"Player {player_number} has joined the lobby {lobby_code}")
                    else:
                        send_message(conn, "LOBBY_FULL_OR_NOT_EXIST")

                elif msg == "quit":
                    connected = False
            except ValueError:
                print(f"[ERROR] An error occurred: invalid message length '{msg_length}'")

    conn.close()
    
    with active_connections_lock:
        active_connections -= 1
        print(f"Active Connections: {active_connections}")

    if lobby_code and conn in lobbies.get(lobby_code, []):
        lobbies[lobby_code].remove(conn)
        if not lobbies[lobby_code]:
            del lobbies[lobby_code]
            print(f"Lobby {lobby_code} closed")

def start():
    global active_connections
    server.listen()
    print(f"Listening on {host}:{port}")
    try:
        while True:
            conn, addr = server.accept()
            with active_connections_lock:
                active_connections += 1
                print(f"Active Connections: {active_connections}")
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print("\nServer is shutting down...")
    finally:
        server.close()

if __name__ == "__main__":
    start()