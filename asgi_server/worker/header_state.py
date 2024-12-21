from http import http_header_parser


class HeaderState:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.running = True

    async def run(self):
        buffer = b""
        while self.running:
            buffer += await self.reader.read(1)
            buffer = self.handle(buffer)
        return self.header

    def handle(self, buffer):
        if len(buffer) > 3 and buffer[-4:] == b"\r\n\r\n":
            self.header = http_header_parser.parse_header(buffer)
            self.running = False
        else:
            return buffer
