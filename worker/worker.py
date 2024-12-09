import logging
from worker.header_state import HeaderState
from worker.asgi_state import AsgiState
from response import response_builder


class Worker:
    def __init__(self, reader, writer, app):
        self.reader = reader
        self.writer = writer
        self.current_state = "HEADER"
        self.peername = self.writer.get_extra_info("socket").getpeername()
        self.header_state = HeaderState(self.reader, self.writer)
        self.asgi_state = AsgiState(
            reader, writer, app, self.peername, "127.0.0.1", 8888
        )

    async def run(self):
        logging.info("New client: %s\n", self.peername)
        header = {}

        while self.current_state != "ENDING":
            logging.info("%s(%s):\n%s\n", self.peername, self.current_state, header)
            match self.current_state:
                case "HEADER":
                    header = await self.header_state.run()
                    self.current_state = "ASGI"
                case "ASGI":
                    print("ASGI")
                    await self.asgi_state.run(header)
                    self.current_state = "ENDING"
                case _:
                    break

    async def teardown(self):
        logging.info("Closing connexion with %s", self.peername)
        self.writer.write(response_builder.closing_message().encode())
        await self.writer.drain()
        logging.info("Connexion closed with %s", self.peername)
