import datetime

PAGE_404 = "./html/404.html"

EXTENSION_MESSAGE = {
    "html": "text/html; charset=utf-8",
    "png": "image/png",
    "jpg": "image/jpg",
    "jpeg": "image/jpeg",
}


class ResponseBuilder:
    def __init__(self, routes):
        self.routes = routes
        self.status = 200

    def make_response(self, header):
        response = b""
        body = self.make_body(header)
        response += self.make_header(len(body), header).encode()
        response += body

        return response

    def make_header(self, length, request_header):
        header = f"HTTP/1.1 {self.status} OK\r\n"
        header += f"Date: {get_time_now()}\r\n"
        header += "Accept_Ranges: bytes\r\n"
        header += f"Content-Length: {length}\r\n"
        header += "Vary: Accept-Encoding\r\n"
        header += f"Content-Type: {self.get_type(request_header)}\r\n\r\n"

        return header

    def get_type(self, request_header):
        extension = request_header["request"]["path"].split(".")[-1]
        if extension == "/":
            return EXTENSION_MESSAGE["html"]
        else:
            return EXTENSION_MESSAGE[extension]

    def make_body(self, request_header):
        path = request_header["request"]["path"]
        if path not in self.routes.keys():
            return self.get_404()
        return self.get_content(self.routes[path])

    def get_content(self, path):
        with open(path, "br") as f:
            content = f.read()
        return content

    def get_404(self):
        return self.get_content(PAGE_404)


def get_time_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d, %b %Y %H:%M:%S GMT")
