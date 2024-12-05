import datetime

PAGE_404 = "./html/404.html"


class ResponseBuilder:
    def __init__(self, routes):
        self.routes = routes
        self.status = 200

    def make_response(self, request):
        response = b""
        body = self.make_body(request.header)
        response += self.make_header(len(body), request).encode()
        response += body

        return response

    def make_header(self, length, request):
        header = f"HTTP/1.1 {self.status} OK\r\n"
        header += f"Date: {get_time_now()}\r\n"
        header += "Accept_Ranges: bytes\r\n"
        header += f"Content-Length: {length}\r\n"
        header += "Vary: Accept-Encoding\r\n"
        header += f"Content-Type: {request.content_type()}\r\n\r\n"

        return header

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
