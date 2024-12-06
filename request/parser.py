class Parser:
    def parse_header(self, data):
        header = data.decode()
        splits = header.strip().split("\r\n")

        header = {}
        header["request"] = self.get_request_line(splits[0])
        for chunk in splits[1:]:
            parts = chunk.split(":")
            header[parts[0].strip().lower()] = parts[1].strip().lower()
        return header

    def get_request_line(self, first_line):
        chunks = first_line.split(" ")
        retval = {
            "method": chunks[0].strip().lower(),
            "path": chunks[1].strip().lower(),
            "protocol": chunks[2].strip().lower(),
        }
        return retval
