from request.body_handler import BodyHandler
from worker.responding_state import RespondingState

MAX_BODY = 1000000


class BodyState:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.running = True

    def state(self):
        return "BODY"

    async def run(self, request):
        if is_content_length(request):
            request.body = await self.reader.read(self.body_size(request))
            self.handle(request)
        return RespondingState(self.reader, self.writer)

    def body_size(self, request):
        retval = 0
        if "content-length" in request.header.keys():
            retval = int(request.header["content-length"])
        else:
            retval = MAX_BODY
        return MAX_BODY if retval > MAX_BODY else retval

    def handle(self, request):
        handler = BodyHandler(request)
        handler.parse()


def is_content_length(request):
    return "content-length" in request.header.keys()


def is_transfer_coding(request):
    return "transfer-encoding" in request.header.keys()
