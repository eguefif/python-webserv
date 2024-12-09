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
    with open("./html/index.html", "r") as f:
        content = f.read()
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/html"],
                [b"content-length", f"{len(content)}".encode()],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": content.encode(),
        }
    )


async def app(scope, receive, send):
    print("test")
    assert scope["type"] == "http"
    print("Incoming: ", scope["path"])

    task = None
    match scope["path"]:
        case "/":
            task = asyncio.create_task(handle_root(send))
        case "/image.jpg":
            task = asyncio.create_task(handle_image(send))

    if task:
        await task
