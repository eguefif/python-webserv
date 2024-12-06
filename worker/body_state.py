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
        if is_body(request):
            buffer = await self.reader.read(self.body_size(request))
            self.handle(request, buffer)
        return RespondingState(self.reader, self.writer)

    def body_size(self, request):
        retval = 0
        if "content-length" in request.header.keys():
            retval = int(request.header["content-length"])
        else:
            retval = MAX_BODY
        return MAX_BODY if retval > MAX_BODY else retval

    def handle(self, request, buffer):
        request.body = buffer
        handler = BodyHandler(request)
        handler.handle()


def is_body(request):
    if request.header["request"]["method"].lower() in [
        "post",
        "update",
        "put",
    ]:
        return True
    else:
        return False
