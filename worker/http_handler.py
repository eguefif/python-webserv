import datetime
from response.chunked_response import send_chunked

STATUS = {
    200: (b"200", b"ok"),
}

ENCODINGS = ["utf-8"]


class HttpAppRunner:
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
        scope["type"] = "http"
        scope["asgi"] = {}
        scope["asgi"]["version"] = "2.0"
        scope["asgi"]["spec_version"] = "2.0"
        scope["http_version"] = header["request-line"]["protocol"].split("/")[1]
        scope["method"] = header["request-line"]["method"]
        scope["path"] = header["request-line"]["path"]
        scope["scheme"] = "http"
        scope["query_string"] = header["request-line"]["query"]
        scope["root_path"] = ""
        scope["headers"] = header["headers"]
        scope["host"] = [self.host, self.port]
        scope["server"] = [self.server_ip, self.port]

        return scope

    async def asgi_receive(self):
        message = {}
        body_length = self.get_body_length()
        if body_length > 0:
            body = await self.reader.read(int(body_length))
            message["type"] = "http.request"
            message["body"] = body
            message["more_body"] = False
            return message

    def get_body_length(self):
        headers = self.request_header.get("headers", {})
        for entry in headers:
            if entry[0].lower() == "content-length":
                return int(entry[1])
        return -1

    async def asgi_send(self, event):
        match event["type"]:
            case "http.response.start":
                self.asgi_header = event["headers"]
                header = self.make_header(event)
                self.writer.write(header)
                await self.writer.drain()
            case "http.response.body":
                await self.dispatch_response_builder(event)

    async def dispatch_response_builder(self, event):
        body = event.get("body", b"")
        more_body = event.get("more_body", False)
        if self.is_content_length() or len(body) == 0:
            self.writer.write(body)
            self.writer.drain()
        else:
            await send_chunked(self.writer, body, more_body)

    def is_content_length(self):
        for entry in self.asgi_header:
            if entry[0].decode().lower() == "content-length":
                return True
        return False

    def make_header(self, send_header):
        code, message = STATUS[200]

        header = b"HTTP/1.1 "
        header += code + b" " + message + b"\r\n"
        header += f"Date: {get_time_now()}\r\n".encode()
        header += "Accept_Ranges: bytes\r\n".encode()
        header += "Server: asgi_webserver\r\n".encode()
        if not self.is_content_length():
            header += b"transfer-encoding: chunked\r\n"
        for entry in send_header["headers"]:
            header += entry[0] + b": " + entry[1] + b"\r\n"
        header += b"}\r\n\r\n"

        return header


def get_time_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d, %b %Y %H:%M:%S GMT")
