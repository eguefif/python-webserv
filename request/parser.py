def parse_header(data):
    header = data.decode()
    splits = header.strip().split("\r\n")

    header = {}
    header["request-line"] = get_request_line(splits[0])
    header["headers"] = []
    for chunk in splits[1:]:
        parts = chunk.split(":")
        header["headers"].append([parts[0].strip().lower(), parts[1].strip().lower()])
    return header


def get_request_line(first_line):
    chunks = first_line.split(" ")
    path = chunks[1].strip().lower()
    if path.find("?") != -1:
        query = path.split("?")[1]
        path = path.split("?")[0]
    else:
        query = ""

    retval = {
        "method": chunks[0].strip().lower(),
        "path": path,
        "query": query,
        "protocol": chunks[2].strip().lower(),
    }
    return retval
