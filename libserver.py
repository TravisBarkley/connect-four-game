#!/usr/bin/env python3

import sys
import selectors
import json
import io
import struct

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            data = self.sock.recv(4096)
            if data:
                self._recv_buffer += data
                return True 
            else:
                print("[INFO] Peer closed connection.")
                return False 
        except Exception as e:
            print(f"[ERROR] Read error: {e}")
            return False

    def _write(self):
        try:
            print(f"[DEBUG] Sending message to {self.addr}")
            sent = self.sock.send(self._send_buffer) 
            self._send_buffer = self._send_buffer[sent:]

            if not self._send_buffer:
                self.selector.modify(self.sock, selectors.EVENT_READ, data=self)
            return True 
        except Exception as e:
            print(f"[ERROR] Write error: {e}")
            return False

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj

    def _create_message(self, *, content_bytes, content_type, content_encoding):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">H", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message

    def _create_response_json_content(self):
        action = self.request.get("action")
        if action == "join":
            welcome_message = """
_______________________________________________________
|                                                     |
|          Welcome to Colossal Connect Four!          |               
|    A game of wits, strategy, and colossal fun!      |
|                                                     |
|                                                     |
|                                                     |
|_____________________________________________________|
            """

            content = {"result": welcome_message}
        else:
            content = {"result": f'Error: invalid action "{action}".'}
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            if not self._read(): 
                self.close()
        if mask & selectors.EVENT_WRITE and self._send_buffer:
           if not self._write(): 
                self.close()

    def read(self):
        self._read()

        if self._jsonheader_len is None:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        print(f"[INFO] Closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock) 
        except Exception as e:
            print(f"[WARNING] Error during unregister: {e}")
        self.sock.close()

    def process_protoheader(self):
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print("received request", repr(self.request), "from", self.addr)
        else:
            # Unsupported content-type for now
            raise ValueError(f"Unsupported content-type: {self.jsonheader['content-type']}")

        # Set selector to listen for write events, we’re done reading.
        self._set_selector_events_mask("w")

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            raise ValueError(f"Unsupported content-type: {self.jsonheader['content-type']}")
        
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message

    def send_json(self, content):
        encoded_content = self._json_encode(content, "utf-8")
        self._send_buffer += encoded_content
        self.selector.modify(self.sock, selectors.EVENT_WRITE, data=self)