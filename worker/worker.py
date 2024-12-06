from request.request import Request
from worker.header_state import HeaderState


class Worker:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.current_state = None
        self.request = Request()

    async def run(self):
        self.current_state = HeaderState(self.reader, self.writer)

        while self.current_state.state() != "ENDING":
            print("State: ", self.current_state.state())
            self.current_state = await self.current_state.run(self.request)
