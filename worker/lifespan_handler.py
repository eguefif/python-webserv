import asyncio


class LifeSpanHandler:
    def __init__(self, app):
        self.app = app
        self.app_state = "INIT"

    async def run(self):
        await self.handle_lifespan()

    async def handle_lifespan(self):
        scope = self.create_lifespan_scope()
        await self.app(scope, self.lifespan_receive, self.lifespan_send)

    async def lifespan_send(self, message):
        print(f"Call to lifespan send: {message}")
        if message["type"] == "lifespan.startup.complete":
            print("App state: UP")
            self.app_state = "RUNNING"
        elif message["type"] == "lifespan.startup.failed":
            print("App state: startup failed")
            self.app_state = "FAILED"

    async def lifespan_receive(self):
        print("Call to lifespan receive")
        if self.app_state == "INIT":
            return {"type": "lifespan.startup"}
        elif self.app_state == "SHUTDOWN":
            return {"type": "lifespan.shutdown"}
        else:
            while self.app_state == "RUNNING":
                await asyncio.sleep(0)
            return {"type": ""}

    def create_lifespan_scope(self):
        scope = self.get_base_scope()
        scope["type"] = "lifespan"

        return scope

    def get_base_scope(self):
        scope = {}
        scope["asgi"] = {}
        scope["asgi"]["version"] = "2.0"
        scope["asgi"]["spec_version"] = "2.0"

        return scope
