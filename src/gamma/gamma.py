import logging
import asyncio
from gamma.netty.player_connection import PlayerConnection
from gamma.netty.server_connection import ServerConnection
from gamma.netty.connection_relay import ConnectionRelay
from gamma.gui.terminal import GammaTerminal
from gamma.mixin.logger import CallbackHandler
# logging.basicConfig = lambda *a, **k: None  # patch first
root = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    handlers=[CallbackHandler()]  # add logging.StreamHandler() for console output
)

class Gamma:
    def __init__(self, host:str='127.0.0.1', port:int=25565):
        self.host = host
        self.port = port

    def start(self):
        asyncio.run(self.start_async())

    async def start_async(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.terminal_task())
            tg.create_task(self.server_task())
    
    async def terminal_task(self):
        interface = GammaTerminal()
        await interface.run_async()
    
    async def server_task(self):
        server = await asyncio.start_server(self.handle_player, self.host, self.port)
        async with server:
            await server.serve_forever()
        

    async def handle_player(self, reader, writer):
        async def _handle(reader, writer):
            try:
                player_conn = PlayerConnection(reader, writer)
                server_conn = ServerConnection(host='localhost', port=25560)
                relay = ConnectionRelay(downstream=player_conn, upstream=server_conn)
                await relay.start()
            except (ConnectionResetError, BrokenPipeError, EOFError, asyncio.CancelledError):
                pass
            finally:
                if not writer.is_closing():
                    writer.close()
        asyncio.create_task(_handle(reader, writer))

