import asyncio


def get_response(header):
    length = len(header) + 2
    h = b"HTTP/1.1 200 OK\r\n"
    h += b"Date: Tue, 3 Dec 2024 21:16:3 EDT\r\n"
    h += b"Accept_Ranges: bytes\r\n"
    h += f"Content-length: #{length}\r\n".encode()
    h += b"Vary: Accept-Encoding\r\n"
    h += b"Content-Type: text/plain\r\n\r\n"
    h += f"{header}\r\n\r\n".encode()
    return h


def get_request(req):
    chunks = req.split(b" ")
    retval = {
        "method": chunks[0].decode().strip(),
        "path": chunks[1].decode().strip(),
        "protocol": chunks[2].decode().strip(),
    }
    return retval


def parse_header(data):
    splits = data.strip().split(b"\r\n")

    header = {}
    header["request"] = get_request(splits[0])
    for chunk in splits[1:]:
        parts = chunk.split(b":")
        header[parts[0].decode().strip()] = parts[1].decode().strip()

    return header


async def handle(reader, writer):
    data = await reader.read(500)
    header = parse_header(data)

    response = get_response(header)
    writer.write(response)

    await writer.drain()
    writer.close()
    await writer.wait_closed()


async def main():
    server = await asyncio.start_server(handle, "127.0.0.1", 8888)
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on #{addrs}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
