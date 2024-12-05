class Error400Exception(Exception):
    def __init__(self, message):
        if message:
            self.message = message
        else:
            self.message = "Bad Request"
        super().__init__(self.message)
