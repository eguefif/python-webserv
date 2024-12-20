import logging
from worker.header_state import HeaderState
from http.http_handler import HttpAppRunner
from websocket.ws_handler import WsAppRunner
from http.response import response_builder


class Worker:
    def __init__(self, reader, writer, app):
        self.reader = reader
        self.writer = writer
        self.current_state = "HEADER"
        self.peername = self.writer.get_extra_info("socket").getpeername()
        self.header_state = HeaderState(self.reader, self.writer)
        self.app = app
        self.host = "127.0.0.1"
        self.port = 8888

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
                    if self.is_http(header):
                        logging.info("Creating http runner")
                        app_runner = HttpAppRunner(
                            self.reader,
                            self.writer,
                            self.app,
                            self.peername,
                            self.host,
                            self.port,
                        )
                        await app_runner.run(header)
                    else:
                        logging.info("Creating ws runner")
                        app_runner = WsAppRunner(
                            self.reader,
                            self.writer,
                            self.app,
                            self.peername,
                            self.host,
                            self.port,
                        )
                        await app_runner.run(header)
                    self.current_state = "ENDING"
                case _:
                    break

    def is_http(self, header):
        for entry in header["headers"]:
            if entry[0] == "sec-websocket-key":
                return False
        return True

    async def teardown(self):
        logging.info("Closing connexion with %s", self.peername)
        self.writer.write(response_builder.closing_message().encode())
        await self.writer.drain()
        logging.info("Connexion closed with %s", self.peername)
