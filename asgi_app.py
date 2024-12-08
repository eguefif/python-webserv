import asyncio


async def handle_image(send):
    with open("./html/image.jpg", "rb") as f:
        image = f.read()

    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"image/png"],
                [b"content-length", f"{len(image)}".encode()],
            ],
        }
    )

    await send(
        {
            "type": "http.response.body",
            "body": image,
        }
    )


async def handle_root(send):
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/html"],
            ],
        }
    )
    with open("./html/index.html", "r") as f:
        content = f.read()
    await send(
        {
            "type": "http.response.body",
            "body": content.encode(),
        }
    )


async def say_hello(msg):
    await asyncio.sleep(5)
    print(msg)


async def app(scope, receive, send):
    assert scope["type"] == "http"
    print("Incoming: ", scope["path"])

    match scope["path"]:
        case "/":
            task = asyncio.create_task(handle_root(send))
        case "/image.jpg":
            task = asyncio.create_task(handle_image(send))
        case _:
            say_hello_task = asyncio.create_task(say_hello("NOTHING TO DO"))

    say_hello_task = asyncio.create_task(say_hello("Hello, World!"))
    await say_hello_task
    if task:
        await task
