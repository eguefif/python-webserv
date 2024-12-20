import asyncio
import hashlib
import base64

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

    async def run(self, header):
        self.request_header = header
        scope = self.create_scope(header)
        self.app_task = asyncio.create_task(
            self.app(scope, self.asgi_receive, self.asgi_send)
        )
        while self.ws_state != "CLOSED":
            await asyncio.sleep(0)

    async def handle_handshake(self):
        key = self.get_key().strip()
        retval_key = self.get_sha1_b64_key(key)
        print(retval_key)
        header = self.make_handshake_header(retval_key)
        print(header)
        self.writer.write(header)
        await self.writer.drain()

    def get_key(self):
        for entry in self.request_header["headers"]:
            if entry[0] == "sec-websocket-key":
                return entry[1]
        return "error"

    def get_sha1_b64_key(self, key):
        print(key)
        retval_key = f"{key}{WS_GUID}"
        print(retval_key)
        hasher = hashlib.sha1()
        hasher.update(retval_key.encode())
        hash = hasher.digest()
        print(hash)
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
        print("App is receiving")
        if self.ws_state == "INIT":
            self.ws_state = "HANDSHAKING"
            return {"type": "websocket.connect"}
        elif self.ws_state == "CLOSED":
            return {"type": "websocket.disconnect"}
        elif self.ws_state == "RUNNING":
            print("reading from socket")

    async def asgi_send(self, message):
        print("App is sending: ", message)
        if self.ws_state == "HANDSHAKING" and message["type"] == "websocket.accept":
            self.ws_state = "RUNNING"
            await self.handle_handshake()
        if self.ws_state == "RUNNING" and message["type"] == "websocket.send":
            print(message)
