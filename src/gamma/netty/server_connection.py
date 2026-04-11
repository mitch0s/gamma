import asyncio
from gamma.netty.connection import Connection


class ServerConnection(Connection):
    def __init__(self, host:str, port:int=25560):
        super().__init__(reader=None, writer=None)
        self.host = host
        self.port = port

    async def connect(self):
        """Opens the TCP connection without starting read/write loops."""
        self.reader, self.writer = await asyncio.open_connection(
            host=self.host, port=self.port
        )

    async def start(self):
        if self.reader is None:
            await self.connect()
        await super().start()