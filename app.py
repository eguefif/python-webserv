import asyncio
import os

from contextlib import asynccontextmanager

from starlette.applications import Starlette
from starlette.routing import WebSocketRoute, Mount
from starlette.staticfiles import StaticFiles
import sqlite3


def get_cursor():
    con = sqlite3.connect("chat.db")
    return con.cursor(), con


def broadcast(message):
    cur, con = get_cursor()
    users = cur.execute("SELECT name FROM users").fetchall()
    for user in users:
        cur.execute(f"INSERT INTO {user[0]} (message) VALUES ('{message}')")
    con.commit()
    cur.close()
    con.close()


def get_user_messages(user):
    cur, con = get_cursor()
    res = cur.execute(f"SELECT message FROM {user}").fetchall()
    cur.execute(f"DELETE FROM {user}")
    con.commit()
    cur.close()
    con.close()
    return [v[0] for v in res]


async def send_messages(websocket, user):
    while True:
        messages = get_user_messages(user)
        for message in messages:
            await websocket.send_text(message)
        await asyncio.sleep(0.1)


async def listening(websocket, user):
    async for message in websocket.iter_text():
        print(message)
        broadcast(message)
        await asyncio.sleep(0.1)
    remove_client(user)
    await websocket.close()
    return False


async def persist_user(websocket):
    cur, con = get_cursor()
    message = await websocket.receive_text()
    print("Persisting user: ", message)
    cur.execute(f"INSERT INTO users (name) VALUES ('{message}')")
    cur.execute(f"CREATE TABLE {message}('message')")
    con.commit()
    cur.close()
    con.close()
    print("User was persisted: ", message)
    return message


def remove_client(client):
    cur, con = get_cursor()
    cur.execute(f"DROP TABLE {client}")
    cur.close()
    con.close()


async def websocket_endpoint(websocket):
    await websocket.accept()
    user = await persist_user(websocket)
    listening_task = asyncio.create_task(listening(websocket, user))
    sending_task = asyncio.create_task(send_messages(websocket, user))
    await listening_task
    await sending_task


@asynccontextmanager
async def lifespan(_):
    print("Startup")
    print("Creating sqlite DB")
    con = sqlite3.connect("chat.db")
    cursor = con.cursor()
    table = cursor.execute("SELECT name FROM sqlite_master").fetchall()
    if ("users",) not in table:
        print("Creating table")
        cursor.execute("CREATE TABLE users(name TEXT)")
    cursor.close()
    con.close()
    print("Initializing over")

    yield

    print("Deleting db")
    os.remove("./chat.db")
    print("Shutdown")


routes = [
    WebSocketRoute("/ws", websocket_endpoint),
    Mount("/", app=StaticFiles(directory="./", html=True), name="homepage"),
]


app = Starlette(debug=True, routes=routes, lifespan=lifespan)
