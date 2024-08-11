from satori.server import Server
from .adapter import Chino_adapter
from .router import Chino_router

server = Server(
    host="0.0.0.0",
    port=8080,
)
server.apply(Chino_adapter())
server.apply(Chino_router())


async def main():
    await server.run_async()
