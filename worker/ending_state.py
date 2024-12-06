class EndingState:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer

    def state(self):
        return "ENDING"

    async def run(self, _):
        return EndingState(self.reader, self.writer)
