class Error400Exception(Exception):
    def __init__(self, message):
        self.status = 400
        if message:
            self.message = message
        else:
            self.message = "Bad Request"
        super().__init__(self.message)


class ErrorUnsupportedMediaTypeException(Exception):
    def __init__(self, message):
        self.status = 415
        if message:
            self.message = message
        else:
            self.message = "Wrong file type"
        super().__init__(self.message)
