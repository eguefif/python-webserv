import datetime

STATUS = {
    200: (b"200", b"ok"),
}


class AsgiState:
    def __init__(self, reader, writer, app):
        self.writer = writer
        self.reader = reader
        self.app = app

    async def run(self, request):
        scope = self.create_scope(request)
        print("scope: ", scope)
        await self.app(scope, self.asgi_receive, self.asgi_send)

    def create_scope(self, request):
        scope = {}
        scope["type"] = "http"
        scope["asgi"] = {}
        scope["asgi"]["version"] = "2.0"
        scope["asgi"]["spec_version"] = "2.0"
        scope["http_version"] = request.header["request-line"]["protocol"].split("/")[1]
        scope["method"] = request.header["request-line"]["method"]
        scope["path"] = request.header["request-line"]["path"]

        return scope

    async def asgi_receive(self, event):
        print("read event: ", event)

    async def asgi_send(self, event):
        match event["type"]:
            case "http.response.start":
                self.header = self.make_header(event)
            case "http.response.body":
                self.body = event["body"]
                await self.send_response()

    async def send_response(self):
        response = self.header
        response += self.body

        self.writer.write(response)
        await self.writer.drain()

    def make_header(self, send_header):
        code, message = STATUS[200]

        header = b"HTTP/1.1 "
        header += code + b" " + message + b"\r\n"
        header += f"Date: {get_time_now()}\r\n".encode()
        header += "Accept_Ranges: bytes\r\n".encode()
        for entry in send_header["headers"]:
            header += entry[0] + b": " + entry[1] + b"\r\n"
        header += b"}\r\n\r\n"

        return header

    def make_body(self, send_body):
        print("body")


def get_time_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d, %b %Y %H:%M:%S GMT")
