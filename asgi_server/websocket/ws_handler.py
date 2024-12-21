import asyncio
import hashlib
import base64

from websocket.frame_parser import FrameParser
from websocket.ws_frame_response import ws_frame_response_builder

ENCODINGS = ["utf-8"]

WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


class WsAppRunner:
    def __init__(self, reader, writer, app, peername, server_ip, port):
        self.writer = writer
        self.reader = reader
        self.app = app
        self.host = peername[0]
        self.port = peername[1]
        self.server_ip = server_ip
        self.port = port
        self.request_header = {}
        self.header = b""
        self.ws_state = "INIT"
        self.ws_messages = []

    async def run(self, header):
        self.request_header = header
        scope = self.create_scope(header)
        self.app_task = asyncio.create_task(
            self.app(scope, self.asgi_receive, self.asgi_send)
        )
        self.reading_task = asyncio.create_task(self.read_socket())
        while self.ws_state != "CLOSED":
            await asyncio.sleep(0)

    async def handle_handshake(self):
        key = self.get_key().strip()
        retval_key = self.get_sha1_b64_key(key)
        header = self.make_handshake_header(retval_key)
        self.writer.write(header)
        await self.writer.drain()

    def get_key(self):
        for entry in self.request_header["headers"]:
            if entry[0] == "sec-websocket-key":
                return entry[1]
        return "error"

    def get_sha1_b64_key(self, key):
        retval_key = f"{key}{WS_GUID}"
        hasher = hashlib.sha1()
        hasher.update(retval_key.encode())
        hash = hasher.digest()
        return base64.b64encode(hash)

    def make_handshake_header(self, key):
        header = "HTTP/1.1 101 Switching Protocols\r\n"
        header += "Upgrade: websocket\r\n"
        header += "Connection: Upgrade\r\n"
        header += "Host: 127.0.0.1:8888\r\n"
        header += "Sec-WebSocket-Version: 13\r\n"
        header += "Sec-WebSocket-Accept: "
        return header.encode() + key + b"\r\n\r\n"

    def create_scope(self, header):
        scope = {}
        scope["asgi"] = {}
        scope["asgi"]["version"] = "2.0"
        scope["asgi"]["spec_version"] = "2.0"
        scope["type"] = "websocket"
        scope["scheme"] = "ws"
        scope["path"] = header["request-line"]["path"]
        scope["raw_path"] = None
        scope["headers"] = header["headers"]
        scope["client"] = [self.host, self.port]
        scope["server"] = [self.server_ip, self.port]

        return scope

    async def asgi_receive(self):
        if self.ws_state == "INIT":
            self.ws_state = "HANDSHAKING"
            return {"type": "websocket.connect"}
        elif self.ws_state == "CLOSED":
            return {"type": "websocket.disconnect"}
            # TODO: implements proper websocket closing mechanism
        elif self.ws_state == "RUNNING":
            while len(self.ws_messages) == 0:
                await asyncio.sleep(0)
            retval = {"type": "websocket.receive"}
            message = self.pop_next_message()
            if message["type"] == "bytes":
                retval["bytes"] = message["content"]
            else:
                retval["text"] = message["content"]
            return retval

    def pop_next_message(self):
        message = self.ws_messages[0]
        for i in range(0, len(self.ws_messages) - 1):
            self.ws_messages[i] = self.ws_messages[i + 1]
        self.ws_messages.pop()
        return message

    async def asgi_send(self, message):
        if self.ws_state == "HANDSHAKING" and message["type"] == "websocket.accept":
            self.ws_state = "RUNNING"
            await self.handle_handshake()
        if self.ws_state == "RUNNING" and message["type"] == "websocket.send":
            print("message: ", message)
            response = ws_frame_response_builder(message)
            self.writer.write(response)
            await self.writer.drain()

    async def read_socket(self):
        frame_parser = FrameParser()
        while self.ws_state != "CLOSED":
            byte = await self.reader.read(1)
            frame_parser.parse(byte)
            if frame_parser.is_frame_complete:
                message = frame_parser.get_message()
                self.ws_messages.append(message)
                frame_parser.reset()
