def parse_header(data):
    header = data.decode()
    splits = header.strip().split("\r\n")

    header = {}
    header["request"] = get_request_line(splits[0])
    for chunk in splits[1:]:
        parts = chunk.split(":")
        header[parts[0].strip().lower()] = parts[1].strip().lower()
    return header


def get_request_line(first_line):
    chunks = first_line.split(" ")
    retval = {
        "method": chunks[0].strip().lower(),
        "path": chunks[1].strip().lower(),
        "protocol": chunks[2].strip().lower(),
    }
    return retval
