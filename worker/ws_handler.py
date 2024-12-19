import asyncio
import hashlib
import base64

ENCODINGS = ["utf-8"]

WS_GUID = "258EAFA5-E914-47DA- 95CA-C5AB0DC85B11"


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

    async def run(self, header):
        self.request_header = header
        await self.handle_handshake(header)
        # scope = self.create_scope(header)
        # await self.app(scope, self.asgi_receive, self.asgi_send)
        while True:
            message = await self.reader.read()
            print(message)
            await asyncio.sleep(0)

    async def handle_handshake(self, header):
        key = header["headers"]["sec-websocket-key"].strip()
        retval_key = self.get_sha1_b64_key(key)
        header = self.make_handshake_header(retval_key)
        self.writer.send(header)
        await self.writer.drain()

    def get_sha1_b64_key(self, key):
        key = f"{key}{WS_GUID}"
        hasher = hashlib.sha1()
        hasher.update(key.encode())
        hash = hasher.digest()
        return base64.b64encode(hash)

    def make_handshake_header(self, key):
        header = "HTTP/1.1 101 Switching Protocols\r\n"
        header += "Upgrade: websocket\r\n"
        header += "Connection: Upgrade\r\n"
        header += f"Sec-Wesocket-Accept: {key}\r\n\r\n"
        return header.encode()

    def create_scope(self, header):
        scope = {}
        scope["type"] = "ws"
        scope["asgi"] = {}
        scope["asgi"]["version"] = "2.0"
        scope["asgi"]["spec_version"] = "2.0"
        scope["headers"] = header["headers"]
        scope["host"] = [self.host, self.port]
        scope["server"] = [self.server_ip, self.port]

        return scope

    async def asgi_receive(self): ...

    async def asgi_send(self): ...
