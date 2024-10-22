#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
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
    message = Message(sel, sock, addr, None)
    sel.register(sock, selectors.EVENT_READ | selectors.EVENT_WRITE, data=message)
    return message

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
message = start_connection(host, port)

try:
    while True:
        action = input("Enter command ('join <code>' or 'quit'): ").strip()
        if action.startswith("join"):
            _, code = action.split()
            request = create_request("join", code)
        elif action == "quit":
            request = create_request("quit")
            message.request = request
            message.queue_request()
            print("Exiting...")
            break
        else:
            print("Unknown command. Try 'join <code>' or 'quit'.")
            continue

        message.request = request  # Assign the request to the message.
        message.queue_request()

        events = sel.select(timeout=1)
        for key, mask in events:
            msg = key.data
            try:
                msg.process_events(mask)
            except Exception as e:
                print(f"Error: {e}")
                msg.close()
                sys.exit(1)

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")
finally:
    sel.close()