import logging
import asyncio
from gamma.netty.player_connection import PlayerConnection
from gamma.config import LocalConfigManager
from gamma.netty.server_connection import ServerConnection
from gamma.netty.connection_relay import ConnectionRelay
from gamma.gui.terminal import GammaTerminal
from gamma.mixin.logger import CallbackHandler
import gamma.common


MSG = """
  ______                                                  
 /      \                                                 
|  $$$$$$\  ______   ______ ____   ______ ____    ______  
| $$ __\$$ |      \ |      \    \ |      \    \  |      \ 
| $$|    \  \$$$$$$\| $$$$$$\$$$$\| $$$$$$\$$$$\  \$$$$$$\\
| $$ \$$$$ /      $$| $$ | $$ | $$| $$ | $$ | $$ /      $$
| $$__| $$|  $$$$$$$| $$ | $$ | $$| $$ | $$ | $$|  $$$$$$$
 \$$    $$ \$$    $$| $$ | $$ | $$| $$ | $$ | $$ \$$    $$
  \$$$$$$   \$$$$$$$ \$$  \$$  \$$ \$$  \$$  \$$  \$$$$$$$
   Created by mitch0s            github.com/mitch0s/gamma/   

--------------------------------------------------------------------\r
"""

logger = logging.getLogger()
logging.basicConfig(level=logging.INFO, handlers=[logging.StreamHandler(), CallbackHandler()])  # add logging.StreamHandler() for console output

class Gamma:
    def __init__(self, host:str='0.0.0.0', port:int=25565):
        self.host = host
        self.port = port
        self._conn_id_counter = 0

    def start(self):
        asyncio.run(self.start_async())

    async def start_async(self):
        logger.info(MSG)
        async with asyncio.TaskGroup() as tg:
            # tg.create_task(self.terminal_task())
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
            player_conn = PlayerConnection(reader, writer)
            server_conn = ServerConnection(host='localhost', port=25560)
            # server_conn = ServerConnection(host='mc.playerservers.com', port=25565)
            relay = ConnectionRelay(id=self._conn_id_counter, downstream=player_conn, upstream=server_conn)
            relay.config_manager = LocalConfigManager()
            self._conn_id_counter += 1
            # gamma.common.connections.append(relay)
            asyncio.create_task(relay.start())
            # except* Exception as error:
            #     logger.debug(str(error))
        asyncio.create_task(_handle(reader, writer))

