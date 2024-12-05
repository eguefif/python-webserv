import traceback
import asyncio
from worker.worker import Worker
from error.exception import Error400Exception, ErrorUnsupportedMediaTypeException
from response import error

routes = {
    "/": "./html/index.html",
    "/image.jpg": "./html/image.jpg",
    "/upload.html": "./html/upload.html",
}


async def handle(reader, writer):
    print()
    print("New request: ", writer.get_extra_info("socket"))
    print()
    worker = Worker(reader, writer, routes)
    try:
        await worker.run()
    except Error400Exception:
        response = error.get_error_message(400)
        writer.write(response.encode())
        await writer.drain()
    except ErrorUnsupportedMediaTypeException:
        response = error.get_error_message(415)
        writer.write(response.encode())
        await writer.drain()
    except Exception as e:
        print(f"Error:{e}")
        print(traceback.format_exc())
        response = error.get_error_message(500)
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
