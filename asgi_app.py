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


async def handle_image_upload(receive, send, scope):
    print("Receiving image")
    more_body = True
    body = b""

    while more_body:
        message = await receive()
        body += message.get("body", b"")
        more_body = message.get("more_body", False)

    print(body)
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                [b"content-type", b"text/plain"],
            ],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": b"File received",
        }
    )


async def app(scope, receive, send):
    assert scope["type"] == "http"
    print("Incoming: ", scope["path"])
    print(scope)

    task = None
    match scope["path"]:
        case "/":
            task = asyncio.create_task(handle_root(send))
        case "/image.jpg":
            task = asyncio.create_task(handle_image(send))
        case "/upload.html":
            task = asyncio.create_task(handle_image_upload(receive, send, scope))

    if task:
        await task
