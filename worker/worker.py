import time
import datetime

MAX_READ = 10000


class Worker:
    def __init__(self, reader, writer, routes):
        self.reader = reader
        self.writer = writer
        self.state = "HEADER"
        self.routes = routes

    async def run(self):
        buffer = b""
        while self.state != "ENDING" and len(buffer) < MAX_READ:
            buffer += await self.reader.read(1)
            buffer = await self.handle_state(buffer)

    async def handle_state(self, buffer):
        if self.state == "HEADER":
            if len(buffer) > 3 and buffer[-4:] == b"\r\n\r\n":
                self.header = self.parse_header(buffer)
                self.state = "BODY"
                buffer = b""

        if self.state == "BODY":
            if not self.is_body():
                self.state = "RESPONDING"
            elif len(buffer) > 3 and buffer[-4:] == b"\r\n\r\n":
                self.body = buffer.decode().strip
                self.state = "RESPONDING"
                buffer = b""

        if self.state == "RESPONDING":
            response = self.make_response()
            self.writer.write(response.encode())
            await self.writer.drain()
            self.state = "ENDING"

        return buffer

    def is_body(self):
        if self.header["request"]["method"] in ["POST", "UPDATE"]:
            return True
        else:
            return False

    def parse_header(self, data):
        header = data.decode()
        splits = header.strip().split("\r\n")

        header = {}
        header["request"] = self.get_request_line(splits[0])
        for chunk in splits[1:]:
            parts = chunk.split(":")
            header[parts[0].strip()] = parts[1].strip()
        return header

    def get_request_line(self, first_line):
        chunks = first_line.split(" ")
        retval = {
            "method": chunks[0].strip(),
            "path": chunks[1].strip(),
            "protocol": chunks[2].strip(),
        }
        return retval

    def make_response(self):
        response = ""
        response += self.make_header()
        response += self.make_body()

        return response

    def make_header(self):
        length = len(self.header) + 2
        header = "HTTP/1.1 200 OK\r\n"
        header += f"Date: {get_time_now()}\r\n"
        header += "Accept_Ranges: bytes\r\n"
        header += f"Content-Length: #{length}\r\n"
        header += "Vary: Accept-Encoding\r\n"
        header += "Content-Type: html\r\n\r\n"

        return header

    def make_body(self):
        path = self.header["request"]["path"]
        if path not in self.routes.keys():
            "error"
        return self.get_content(self.routes[path])

    def get_content(self, path):
        with open(path, "r") as f:
            content = f.read()
        return content


def get_time_now():
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%a, %d, %b %Y %H:%M:%S GMT")
