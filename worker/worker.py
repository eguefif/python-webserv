from worker.parser import Parser
from worker.response_builder import ResponseBuilder

MAX_READ = 10000


class Worker:
    def __init__(self, reader, writer, routes):
        self.reader = reader
        self.writer = writer
        self.state = "HEADER"
        self.parser = Parser()
        self.response_builder = ResponseBuilder(routes)
        self.message = None

    async def run(self):
        buffer = b""
        while self.state != "ENDING" and len(buffer) < MAX_READ:
            buffer += await self.reader.read(1)
            buffer = await self.handle_state(buffer)

    async def handle_state(self, buffer):
        if self.state == "HEADER":
            if len(buffer) > 3 and buffer[-4:] == b"\r\n\r\n":
                self.header = self.parser.parse_header(buffer)
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
            response = self.response_builder.make_response(self.header)
            self.writer.write(response.encode())
            await self.writer.drain()
            self.state = "ENDING"

        return buffer

    def is_body(self):
        if self.header["request"]["method"] in ["POST", "UPDATE"]:
            return True
        else:
            return False
