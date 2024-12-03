#!/usr/bin/env python3

import time
import socket
import threading
import random
import string
import argparse

parser = argparse.ArgumentParser(description="Server for listening to client connections.")
parser.add_argument('-p', '--port', required=True, type=int, help="Listening port of the server")
args = parser.parse_args()

host = '0.0.0.0'
port = args.port
ADDR = (host, port)
HEADER = 64

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

active_connections_lock = threading.Lock()
active_connections = 0
lobbies = {
    "lobby_code": {
        "players": [],
        "board": None,
        "current_turn": None,
        "wins": [0, 0]  
    }
}

def generate_game_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

def send_message(conn, message):
    message = message.encode("utf-8")
    msg_length = len(message)
    send_length = f"{msg_length:<{HEADER}}".encode("utf-8")
    payload = send_length + message
    conn.sendall(payload)

def initialize_board():
    return [[' ' for _ in range(7)] for _ in range(6)]

def print_board(board):
    board_str = " \n"
    board_str += "\n".join(["|".join(row) for row in board])
    board_str += "\n0 1 2 3 4 5 6\n"
    board_str += "\n- move <column> - to place a chip\n"
    return board_str

def check_winner(board, player):
    for row in range(6):
        for col in range(7):
            if col + 3 < 7 and all(board[row][col + i] == player for i in range(4)):
                return True
            if row + 3 < 6 and all(board[row + i][col] == player for i in range(4)):
                return True
            if col + 3 < 7 and row + 3 < 6 and all(board[row + i][col + i] == player for i in range(4)):
                return True
            if col - 3 >= 0 and row + 3 < 6 and all(board[row + i][col - i] == player for i in range(4)):
                return True
    return False

def handle_client(conn, addr):
    global active_connections
    print(f"New Client Connected: {addr}.")
    connected = True
    lobby_code = None
    player_name = None
    players = []
    player_names = ["Player 1", "Player 2"]
    while connected:
        try:
            msg_length = conn.recv(HEADER).decode("utf-8").strip()
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode("utf-8")
                print(f"[{addr}] {msg}")
                if msg.startswith("CREATE_LOBBY"):
                    lobby_code = generate_game_code()
                    lobbies[lobby_code] = {
                        "players": [],
                        "board": initialize_board(),
                        "current_turn": None,
                        "wins": [0, 0]
                    }
                    send_message(conn, f"LOBBY_CREATED {lobby_code}")
                    print(f"Lobby {lobby_code} created by {addr}")
                elif msg.startswith("JOIN_LOBBY"):
                    lobby_code = msg.split()[1]
                    if lobby_code in lobbies and len(lobbies[lobby_code]["players"]) < 2:
                        lobbies[lobby_code]["players"].append((conn, addr, "Player"))
                        players = [client[0] for client in lobbies[lobby_code]["players"]]
                        player_number = len(lobbies[lobby_code]["players"])
                        send_message(conn, f"JOINED_LOBBY {lobby_code}")
                        send_message(conn, f"You are Player {player_number}")
                        print(f"{addr} joined lobby {lobby_code} as Player {player_number}")
                        for client, _, _ in lobbies[lobby_code]["players"]:
                            if client != conn:
                                send_message(client, f"Player {player_number} has joined the lobby {lobby_code}")
                    else:
                        send_message(conn, "LOBBY_FULL_OR_NOT_EXIST")
                elif msg == "VIEW_PLAYERS":
                    lobby_code = None
                    for code, lobby in lobbies.items():
                        for client, _, _ in lobby["players"]:
                            if client == conn:
                                lobby_code = code
                                break
                        if lobby_code:
                            break
                    if lobby_code:
                        player_list = [f"{name} (Wins: {wins})" for (_, _, name), wins in zip(lobbies[lobby_code]["players"], lobbies[lobby_code]["wins"])]
                        send_message(conn, f"Players in lobby: {', '.join(player_list)}")
                    else:
                        send_message(conn, "ERROR: You are not in any lobby")
                elif msg.startswith("SET_NAME"):
                    player_name = msg.split()[1]
                    for i, (client, client_addr, _) in enumerate(lobbies[lobby_code]["players"]):
                        if client == conn:
                            lobbies[lobby_code]["players"][i] = (client, client_addr, player_name)
                            player_names[i] = player_name
                            send_message(conn, f"Name set to {player_name}")
                            break
                elif msg == "START_GAME":
                    if lobby_code in lobbies and len(lobbies[lobby_code]["players"]) == 2:
                        players = [client[0] for client in lobbies[lobby_code]["players"]]
                        starter_index = players.index(conn)
                        lobbies[lobby_code]["current_turn"] = starter_index
                        lobbies[lobby_code]["board"] = initialize_board()
                        for client, _, _ in lobbies[lobby_code]["players"]:
                            send_message(client, f"Game starting in 5 seconds. Started by {player_names[starter_index]}.")
                        time.sleep(5)
                        for client, _, _ in lobbies[lobby_code]["players"]:
                            send_message(client, "Game has started!")
                            send_message(client, print_board(lobbies[lobby_code]["board"]))
                            send_message(client, f"{player_names[lobbies[lobby_code]['current_turn']]}'s turn.")
                    else:
                        send_message(conn, "Cannot start game. Lobby must have 2 players.")
                elif msg.startswith("MOVE"):
                    if lobby_code not in lobbies or lobbies[lobby_code]["current_turn"] is None:
                        send_message(conn, "Error: Game not started.")
                        continue
                    
                    current_turn = lobbies[lobby_code]["current_turn"]
                    board = lobbies[lobby_code]["board"]
                    players = [client[0] for client in lobbies[lobby_code]["players"]]
                    player_names = [client[2] for client in lobbies[lobby_code]["players"]]
                
                    if conn == players[current_turn]:
                        try:
                            column = int(msg.split()[1])
                            if column < 0 or column >= 7 or board[0][column] != ' ':
                                send_message(conn, "Invalid move. Try again.")
                            else:
                                for row in range(5, -1, -1):
                                    if board[row][column] == ' ':
                                        board[row][column] = 'X' if current_turn == 0 else 'O'
                                        break
                                    
                                if check_winner(board, 'X' if current_turn == 0 else 'O'):
                                    for client in players:
                                        send_message(client, print_board(board))
                                        send_message(client, f"{player_names[current_turn]} wins!")
                                    lobbies[lobby_code]["wins"][current_turn] += 1
                                    lobbies[lobby_code]["board"] = initialize_board()
                                    lobbies[lobby_code]["current_turn"] = None
                                    for client in players:
                                        send_message(client, "Game over! Type 'start' to play again.")
                                else:
                                    lobbies[lobby_code]["current_turn"] = 1 - current_turn
                                    current_turn = lobbies[lobby_code]["current_turn"]
                                    for client in players:
                                        send_message(client, print_board(board))
                                        send_message(client, f"{player_names[current_turn]}'s turn.")
                        except ValueError:
                            send_message(conn, "Invalid move. Column must be a number.")
                    else:
                        send_message(conn, "It's not your turn.")
                elif msg == "quit":
                    connected = False
        except Exception as e:
            print(f"[ERROR] {e}")
            connected = False
    conn.close()
    with active_connections_lock:
        active_connections -= 1
        print(f"Active Connections: {active_connections}")
    if lobby_code and conn in [client[0] for client in lobbies.get(lobby_code, {}).get("players", [])]:
        lobbies[lobby_code]["players"] = [
            client for client in lobbies[lobby_code]["players"] if client[0] != conn
        ]
        if not lobbies[lobby_code]["players"]:
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
