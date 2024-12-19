ENCODINGS = ["utf-8"]


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
        scope = self.create_scope(header)
        await self.app(scope, self.asgi_receive, self.asgi_send)

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
