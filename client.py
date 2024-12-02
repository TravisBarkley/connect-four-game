#!/usr/bin/env python3
import socket
import sys
import threading

host, port = sys.argv[1], int(sys.argv[2])
HEADER = 64
ADDR = (host, port)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

stop_receiving = threading.Event()
joined_lobby = threading.Event()

def send(msg):
    message = msg.encode("utf-8")
    msg_length = len(message)
    send_length = str(msg_length).encode("utf-8")
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

def receive():
    while not stop_receiving.is_set():
        try:
            msg_length_data = b""
            while len(msg_length_data) < HEADER:
                chunk = client.recv(HEADER - len(msg_length_data))
                if not chunk:
                    raise ConnectionError("Connection lost or server closed connection")
                msg_length_data += chunk

            msg_length_data = msg_length_data.decode("utf-8").strip()

            if msg_length_data.isdigit():
                msg_length = int(msg_length_data)

                msg_data = b""
                while len(msg_data) < msg_length:
                    chunk = client.recv(msg_length - len(msg_data))
                    if not chunk:
                        raise ConnectionError("Connection lost or server closed connection")
                    msg_data += chunk

                msg = msg_data.decode("utf-8")
                print(f"[SERVER] {msg}")

                if msg.startswith("You are Player"):
                    joined_lobby.set()
            else:
                print(f"[ERROR] An error occurred: invalid message header '{msg_length_data}'")
        except Exception as e:
            if not stop_receiving.is_set():
                print(f"[ERROR] An error occurred: {e}")
            break

def print_commands():
    print("Welcome to Connect Four!")
    print("Available commands:")
    print("- create - Create a new lobby")
    print("- join <game_code> - Join an existing lobby")
    print("- quit - Quit the client")

def print_lobby_commands():
    print("Lobby commands:")
    print("- view - View player list")
    print("- name <new_name> - Set your player name")
    print("- start - Start the game")
    print("- quit - Quit the lobby")

receive_thread = threading.Thread(target=receive)
receive_thread.start()

print_commands()
try:
    while True:
        msg = input()
        if msg.lower() == "quit":
            send(msg)
            stop_receiving.set()
            receive_thread.join()
            client.close()
            break
        elif msg.lower() == "create":
            send("CREATE_LOBBY")
        elif msg.lower().startswith("join"):
            _, game_code = msg.split()
            send(f"JOIN_LOBBY {game_code}")
            joined_lobby.wait()  # Wait until the player has joined the lobby
            print_lobby_commands()
            while True:
                lobby_msg = input()
                if lobby_msg.lower() == "quit":
                    send(lobby_msg)
                    stop_receiving.set()
                    receive_thread.join()
                    client.close()
                    break
                elif lobby_msg.lower() == "view":
                    send("VIEW_PLAYERS")
                elif lobby_msg.lower().startswith("name"):
                    _, new_name = lobby_msg.split()
                    send(f"SET_NAME {new_name}")
                elif lobby_msg.lower() == "start":
                    send("START_GAME")
                elif lobby_msg.lower().startswith("move"):
                    _, column = lobby_msg.split()
                    send(f"MOVE {column}")
                else:
                    send(lobby_msg)
        else:
            send(msg)
except Exception as e:
    print(f"[ERROR] {e}")
finally:
    stop_receiving.set()
    receive_thread.join()
    client.close()