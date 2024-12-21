from error.exception import Error400Exception
from error.exception import ErrorUnsupportedMediaTypeException
import re

FILE_PATH = "./uploaded_files/"


class MultipartChunk:
    def __init__(self):
        self.content = b""
        self.header = {}

    def set_header(self, header_chunk):
        splits = [split.decode() for split in header_chunk.split(b"\r\n")]

        for split in splits:
            parts = [split.strip().lower() for split in split.split(":")]
            self.header[parts[0]] = parts[1]

    def process(self):
        if "content-type" in self.header:
            match self.header["content-type"]:
                case "image/png":
                    filename = self.get_filename()
                    with open(FILE_PATH + filename, "bw") as f:
                        f.write(self.content)

                case _:
                    print("BODY: ", self.content.decode())
        else:
            print("BODY: ", self.content.decode())

    def get_filename(self):
        splits = [
            split.strip() for split in self.header["content-disposition"].split(";")
        ]
        for part in splits:
            chunks = part.split("=")
            if chunks[0] == "filename":
                return chunks[1].replace('"', "")
        raise Error400Exception("Bad filename")


class BodyHandler:
    def __init__(self, header, body_content):
        self.header = header
        self.bound_check = self.get_bound_check()
        self.body_content = body_content
        self.body = []

    def get_bound_check(self):
        try:
            return self.header["content-type"].split("boundary=")[1]
        except Exception:
            raise Error400Exception("Bad content-type")

    def get_body_content(self):
        start_index = self.body_content.find(b"\r\n\r\n") + 4
        end_index = self.body_content.find(f"\r\n{self.bound_check}--\r\n".encode())
        if end_index == -1:
            raise Error400Exception("Wrong bound check")
        return self.body_content[start_index:end_index]

    def parse(self):
        sep = b"\r\n\r\n"
        splits = [
            split.strip()
            for split in self.body_content.split(self.bound_check.encode())
        ]
        for split in splits:
            if split == b"--" or split == b"--\r\n\r\n":
                continue
            body_chunks = split.split(sep)
            chunk = MultipartChunk()
            chunk.set_header(body_chunks[0])
            chunk.content = body_chunks[1]
            chunk.process()
            self.body.append(chunk)


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
