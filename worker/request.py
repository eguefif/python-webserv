EXTENSION_MESSAGE = {
    "html": "text/html; charset=utf-8",
    "png": "image/png",
    "jpg": "image/jpg",
    "jpeg": "image/jpeg",
}


class Request:
    def __init__(self):
        self.header = {}
        self.body = ""

    @property
    def content_type(self):
        extension = self.header["request"]["path"].split(".")[-1]
        if extension == "/":
            return EXTENSION_MESSAGE["html"]
        else:
            return EXTENSION_MESSAGE[extension]
