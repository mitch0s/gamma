import asyncio
from gamma.netty.connection import Connection


class ServerConnection(Connection):
    def __init__(self, host:str=None, port:int=25565):
        super().__init__(reader=None, writer=None)
        self.host = host
        self.port = port
    
    async def start(self):
        self.reader, self.writer = await asyncio.open_connection(host=self.host, port=self.port)
        await super().start()
        