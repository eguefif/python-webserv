from request import parser
from worker.body_state import BodyState


class HeaderState:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.running = True

    def state(self):
        return "HEADER"

    async def run(self, request):
        buffer = b""
        while self.running:
            buffer += await self.reader.read(1)
            buffer = self.handle(buffer, request)
        return BodyState(self.reader, self.writer)

    def handle(self, buffer, request):
        if len(buffer) > 3 and buffer[-4:] == b"\r\n\r\n":
            request.header = parser.parse_header(buffer)
            self.running = False
        else:
            return buffer
