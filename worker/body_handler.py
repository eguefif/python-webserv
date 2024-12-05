from error.exception import Error400Exception
from error.exception import ErrorUnsupportedMediaTypeException
import re

FILE_PATH = "./files/"


class BodyHandler:
    def __init__(self, request):
        self.request = request
        self.content_type, self.content_disposition, self.bound_check = (
            self.parse_body_header()
        )
        self.body_content = self.get_body_content()
        self.size = int(self.request.header["content-length"])

    def parse_body_header(self):
        end_body_header = self.request.body.find(b"\r\n\r\n")
        if end_body_header == -1:
            raise Error400Exception("Wrong body")
        body_header = self.request.body[:end_body_header].decode()

        chunks = body_header.split("\r\n")

        return (
            get_type(chunks[2]),
            get_disposition(chunks[1]),
            chunks[0],
        )

    def get_body_content(self):
        start_index = self.request.body.find(b"\r\n\r\n") + 4
        end_index = self.request.body.find(f"\r\n{self.bound_check}--\r\n".encode())
        if end_index == -1:
            raise Error400Exception("Wrong bound check")
        return self.request.body[start_index:end_index]

    def handle(self):
        with open(FILE_PATH + self.content_disposition["filename"], "bw") as f:
            f.write(self.body_content)


def get_disposition(disposition):
    chunks = disposition.split(":")[1].split(";")
    return {
        "name": chunks[1].split("=")[1].replace('"', ""),
        "filename": chunks[2].split("=")[1].replace('"', ""),
    }


def get_type(content_type):
    match = re.findall(r"jpg|png|jpeg", content_type)
    if len(match) == 0:
        raise ErrorUnsupportedMediaTypeException("Handle only image")
    return match[0]
