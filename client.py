#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import struct

import libclient

sel = selectors.DefaultSelector()

def create_request(action):
    return dict(
        type="text/json",
        encoding="utf-8",
        content=dict(action=action),
    )


def start_connection(host, port):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, None)
    sel.register(sock, events, data=message)
    return message

if len(sys.argv) != 3:
    print("Usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
message = start_connection(host, port)

try:
    while True:
        action = input("Enter command (or 'quit' to exit): ").strip()
        request = create_request(action)
        message.request = request
        message.queue_request()  

        events = sel.select(timeout=1)
        for key, mask in events:
            msg = key.data
            try:
                msg.process_events(mask)
            except Exception:
                print(f"main: error: exception for {msg.addr}:\n{traceback.format_exc()}")
                msg.close()

        if action == "quit":
            print("Exiting...")
            break

except KeyboardInterrupt:
    print("Caught keyboard interrupt, exiting")

finally:
    sel.close()
