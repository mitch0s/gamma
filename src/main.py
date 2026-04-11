import logging
from gamma.mixin.logger import CallbackHandler
# logging.basicConfig = lambda *a, **k: None  # patch first
root = logging.getLogger()
logging.basicConfig(
    level=logging.INFO,
    handlers=[CallbackHandler()]  # add logging.StreamHandler() for console output
)

import asyncio
from gamma.netty.player_connection import PlayerConnection
from gamma.netty.server_connection import ServerConnection
from gamma.netty.connection_relay import ConnectionRelay
from gamma.gui.terminal import GammaTerminal

async def server_task(): 
    async def handle_player(reader, writer):
        asyncio.create_task(_handle(reader, writer))

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

    server = await asyncio.start_server(handle_player, '0.0.0.0', 25565)
    async with server:
        await server.serve_forever()

async def terminal_task():
    interface = GammaTerminal()
    await interface.run_async()

async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(terminal_task())
        tg.create_task(server_task())
        root.error('TEST')


if __name__ == '__main__':
    asyncio.run(main())