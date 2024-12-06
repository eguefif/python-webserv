from response.response_builder import ResponseBuilder
from worker.ending_state import EndingState


class RespondingState:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.response_builder = ResponseBuilder()
        self.running = True

    def state(self):
        return "RESPONDING"

    async def run(self, request):
        response = self.response_builder.make_response(request)
        self.writer.write(response)
        await self.writer.drain()
        return EndingState(self.reader, self.writer)
