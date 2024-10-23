#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import json
import struct

from libclient import Message

sel = selectors.DefaultSelector()

def create_request(action, code=None):
    content = {"action": action}
    if code:
        content["code"] = code
    return {"type": "text/json", "encoding": "utf-8", "content": content}


def start_connection(host, port):
    addr = (host, port)
    print(f"Starting connection to {addr}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    sel.register(sock, selectors.EVENT_READ, data=None)
    return sock

def receive_message(sock):
    try:
        events = sel.select(timeout=1)
        for key, mask in events:
            if mask & selectors.EVENT_READ:
                data = sock.recv(4096)
                if data:
                    msg = json.loads(data.decode("utf-8"))
                    print(f"Server response: {msg['content']}")
                else:
                    print("[INFO] Server closed the connection.")
                    sock.close()
                    return
    except Exception as e:
        print(f"[ERROR] Failed to receive message: {e}")

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
sock = start_connection(host, port)
receive_message(sock)
try:
    while True:
        action = input("Enter command ('join <code>' or 'quit'): ").strip()
        if action.startswith("join"):
            _, code = action.split()
            request = {
                "type": "text/json",
                "encoding": "utf-8",
                "content": {"action": "join", "code": code}
            }
            message = Message(sel, sock, addr=None, request=request)
            message.queue_request()

        elif action == "quit":
            request = {
                "type": "text/json",
                "encoding": "utf-8",
                "content": {"action": "quit"}
            }
            message = Message(sel, sock, addr=None, request=request)
            message.queue_request()
            print("Exiting...")
            break

        else:
            print("Unknown command. Try 'join <code>' or 'quit'.")
except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()