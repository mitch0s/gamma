import asyncio
import logging
import time
from gamma.packet import Packet
from gamma.netty.connection import Connection
from gamma.netty.player_connection import PlayerConnection, PlayerConnectionType
from gamma.netty.server_connection import ServerConnection
from gamma.packet.player_handshake_handler import PlayerHandshakePacketHandler
from gamma.response.invalid_hostname_motd import invalid_hostname_motd
from gamma.response.invalid_hostname_disconnect import invalid_hostname_disconnect
import traceback

logger = logging.getLogger()


class ConnectionRelay:
    def __init__(self, id: int, downstream:PlayerConnection, upstream:ServerConnection):
        self.id = id
        self.created_ts = time.time()
        self.downstream = downstream
        self.upstream = upstream
        self.total_packets = 0
        self.total_bytes = 0
        self._connection_open = True

    async def start(self):
        logger.debug('Connection opened.')
        PlayerHandshakePacketHandler(self.downstream)
        try:
            await self._wait_for_handshake_then_relay()
        except* Exception as e:
            logger.debug(str(e))
        finally:
            await self.downstream.close()
            await self.upstream.close()
            logger.debug('Connection closed.')
            if self.downstream.type == PlayerConnectionType.PLAY:
                logger.info(f'{self.downstream.username} ({self.downstream.host_addr}:{self.downstream.host_port}) LEFT {self.downstream.hostname}')
            self._connection_open = False

    async def _wait_for_handshake_then_relay(self):
        async with asyncio.TaskGroup() as tg:
            # create downstream connection class
            tg.create_task(self.downstream.start())

            while True:
                if self.downstream.type and self.downstream.hostname:
                    break
                await asyncio.sleep(0.01)

            invalid_hostname = self.downstream.hostname == 'localhost'
            if invalid_hostname:
                if self.downstream.type == PlayerConnectionType.PING:
                    logger.info(f'Player ({self.downstream.host_addr}:{self.downstream.host_port}) PINGED INVALID HOSTNAME: {self.downstream.hostname}')
                    self.downstream.writer.write(invalid_hostname_motd())
                if self.downstream.type == PlayerConnectionType.PLAY:
                    logger.info(f'Player ({self.downstream.host_addr}:{self.downstream.host_port}) JOINED INVALID HOSTNAME: {self.downstream.hostname}')
                    self.downstream.writer.write(invalid_hostname_disconnect())
                await self.downstream.writer.drain()
                await self.downstream.close()


            if self.downstream.type == PlayerConnectionType.PING:
                logger.info(f'Player ({self.downstream.host_addr}:{self.downstream.host_port}) PINGED {self.downstream.hostname}')
            if self.downstream.type == PlayerConnectionType.PLAY:
                logger.info(f'{self.downstream.username} ({self.downstream.host_addr}:{self.downstream.host_port}) JOINED {self.downstream.hostname}')
            
            tg.create_task(self._forward(self.downstream, self.upstream))
            tg.create_task(self._forward(self.upstream, self.downstream))
            tg.create_task(self.upstream.start())

    async def _forward(self, src: Connection, dst: Connection):
        while True:
            packet:Packet = await src.read()
            await dst.write(packet)
            self.total_packets += 1
            self.total_bytes += len(packet.data)
