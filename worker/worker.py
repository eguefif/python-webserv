from worker.request import Request
from worker.parser import Parser
from worker.response_builder import ResponseBuilder

MAX_READ = 10000
MAX_BODY = 1000000


class Worker:
    def __init__(self, reader, writer, routes):
        self.reader = reader
        self.writer = writer
        self.state = "HEADER"
        self.parser = Parser()
        self.response_builder = ResponseBuilder(routes)
        self.request = Request()

    async def run(self):
        buffer = b""
        while self.state != "ENDING" and len(buffer) < MAX_READ:
            if self.state == "BODY" and self.is_body():
                buffer += await self.reader.read(self.body_size())
            elif self.state == "HEADER":
                buffer += await self.reader.read(1)
            buffer = await self.handle_state(buffer)
        print("Request handling ending")

    def body_size(self):
        retval = 0
        if "content-length" in self.request.header.keys():
            retval = int(self.request.header["content-length"])
        else:
            retval = MAX_BODY
        return MAX_BODY if retval > MAX_BODY else retval

    async def handle_state(self, buffer):
        if self.state == "HEADER":
            if len(buffer) > 3 and buffer[-4:] == b"\r\n\r\n":
                self.request.header = self.parser.parse_header(buffer)
                self.state = "BODY"
                print(f"Receive request: {self.request.header}")
                print()
                buffer = b""

        elif self.state == "BODY":
            if not self.is_body():
                self.state = "RESPONDING"
            else:
                self.request.body = buffer.decode().strip()
                self.state = "RESPONDING"
                buffer = b""

        elif self.state == "RESPONDING":
            response = self.response_builder.make_response(self.request)
            self.writer.write(response)
            response = self.response_builder.make_response(self.request)
            await self.writer.drain()
            self.state = "ENDING"

        return buffer

    def is_body(self):
        if self.request.header["request"]["method"].lower() in ["post", "update"]:
            return True
        else:
            return False
