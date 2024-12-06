import logging
from request.request import Request
from worker.header_state import HeaderState


class Worker:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.current_state = None
        self.request = Request()
        self.peername = self.writer.get_extra_info("socket").getpeername()

    async def run(self):
        logging.info("New client: %s\n", self.peername)
        self.current_state = HeaderState(self.reader, self.writer)

        while self.current_state.state() != "ENDING":
            logging.info(
                "%s(%s):\n%s\n", self.peername, self.current_state.state(), self.request
            )
            self.current_state = await self.current_state.run(self.request)
