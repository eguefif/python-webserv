async def send_chunked(writer, body, more_body):
    length = f"{len(body)}".encode()
    writer.write(length + b"\r\n")
    await writer.drain()
    writer.write(body)
    await writer.drain()

    if not more_body:
        writer.write(b"0\r\n")
        await writer.drain()

