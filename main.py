import importlib
import sys
import signal
import traceback
import asyncio
from worker.worker import Worker
from response import error
import logging


workers = []


def get_app_from_argv():
    if len(sys.argv) == 0:
        print("Usage: python3 main.py module:function")
        return
    mod, _, fct = sys.argv[1].partition(":")

    module = importlib.import_module(mod)
    return getattr(module, fct)


async def handle(reader, writer):
    app = get_app_from_argv()
    worker = Worker(reader, writer, app)
    workers.append(worker)
    try:
        await asyncio.wait_for(worker.run(), timeout=15)
    except asyncio.TimeoutError:
        logging.info("Connection timeout: %s - CLOSING", worker.peername)
    except Exception as e:
        logging.error("Error: %s", e)
        logging.error("Error: %s", traceback.format_exc())
        response = error.get_error_message(e)
        writer.write(response.encode())
        await writer.drain()
    finally:
        writer.close()
        await writer.wait_closed()
        workers.remove(worker)


async def teardown(signal, loop):
    logging.info(f"Receive signal: {signal}")
    logging.info("Shutting Down server")
    for worker in workers:
        await worker.teardown()
    loop.stop()


def set_signal_handling(loop):
    signals = [signal.SIGINT, signal.SIGTERM, signal.SIGHUP]
    for sig in signals:
        loop.add_signal_handler(
            sig, lambda sig=sig: asyncio.create_task(teardown(sig, loop))
        )


async def main():
    logging.basicConfig(level=logging.DEBUG, encoding="utf-8")

    server = await asyncio.start_server(handle, "127.0.0.1", 8888)

    loop = server.get_loop()
    set_signal_handling(loop)

    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    print(f"Serving on #{addrs}")

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
