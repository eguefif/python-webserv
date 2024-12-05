import asyncio
from worker.worker import Worker
from worker.response_builder import get_time_now
from worker.exception import Error400Exception

routes = {"/": "./html/index.html"}

PAGE_500 = "./html/500.html"
PAGE_400 = "./html/400.html"


def get_header(length, error):
    header = f"HTTP/1.1 {error} OK\r\n"
    header += f"Date: {get_time_now()}\r\n"
    header += "Accept_Ranges: bytes\r\n"
    header += f"Content-Length: {length}\r\n"
    header += "Vary: Accept-Encoding\r\n"
    header += "Content-Type: html\r\n\r\n"
    return header


def get_body(path):
    with open(path, "r") as f:
        content = f.read()
    return content


def get_error_message(error):
    path = PAGE_500 if error == 500 else PAGE_400
    body = get_body(path)
    response = get_header(len(body), 500)
    response += body
    return response


async def handle(reader, writer):
    worker = Worker(reader, writer, routes)
    try:
        await worker.run()
    except Error400Exception:
        response = get_error_message(400)
        writer.write(response.encode())
        await writer.drain()
    except Exception:
        response = get_error_message(500)
        writer.write(response.encode())
        await writer.drain()
    finally:
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
