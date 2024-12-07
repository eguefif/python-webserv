from response.response_builder import ResponseBuilder


class RespondingState:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.response_builder = ResponseBuilder()
        self.running = True

    def state(self):
        return "RESPONDING"

    async def run(self, request):
        from worker.header_state import HeaderState
        from worker.ending_state import EndingState

        response = self.response_builder.make_response(request)
        self.writer.write(response)
        await self.writer.drain()

        if self.is_closing(request):
            return EndingState(self.reader, self.writer)
        return HeaderState(self.reader, self.writer)

    def is_closing(self, request):
        if "connection" in request.header.keys():
            if request.header["connection"] == "clone":
                return True
        return False
