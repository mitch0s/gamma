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
    def __init__(self, id: int, downstream: PlayerConnection, upstream: ServerConnection):
        self.id = id
        self.created_ts = time.time()
        self.downstream = downstream
        self.upstream = upstream
        self.total_packets = 0
        self.total_bytes = 0

    async def start(self):
        logger.info('Connection opened.')
        try:
            PlayerHandshakePacketHandler(self.downstream)
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.downstream.start())
                tg.create_task(self._wait_for_handshake_then_relay())
        except* Exception as eg:
            for e in eg.exceptions:
                logger.debug('ConnectionRelay error: %s', e)
        finally:
            await self.downstream.close()
            await self.upstream.close()
            logger.info('Connection closed.')

    async def _wait_for_handshake_then_relay(self):
        while True:
            if self.downstream.type and self.downstream.hostname:
                break
            await asyncio.sleep(0.01)

        invalid_hostname = self.downstream.hostname == 'localhost'

        if invalid_hostname:
            if self.downstream.type == PlayerConnectionType.PING:
                self.downstream.writer.write(invalid_hostname_motd())
                await self.downstream.writer.drain()
                ping = await self.downstream.read()
                if ping:
                    self.downstream.writer.write(ping.data)
                    await self.downstream.writer.drain()
            elif self.downstream.type == PlayerConnectionType.PLAY:
                self.downstream.writer.write(invalid_hostname_disconnect())
                await self.downstream.writer.drain()
            return

        # valid hostname — connect upstream and relay
        await self.upstream.connect()
        while True:
            packet = self.downstream.read_nowait()
            if packet is None:
                break
            self.upstream.writer.write(packet.data)
        await self.upstream.writer.drain()

        async with asyncio.TaskGroup() as tg:
            tg.create_task(self.upstream.start())
            tg.create_task(self._forward(self.downstream, self.upstream))
            tg.create_task(self._forward(self.upstream, self.downstream))

    async def _forward(self, src: Connection, dst: Connection):
        while True:
            packet: Packet = await src.read()
            if not packet:
                break
            await dst.write(packet)
            self.total_packets += 1
            self.total_bytes += len(packet.data)
        await src.close()
        await dst.close()

    async def _forward(self, src: Connection, dst: Connection):
        while True:
            packet: Packet = await src.read()
            if not packet:
                break
            await dst.write(packet)
            self.total_packets += 1
            self.total_bytes += len(packet.data)
        await src.close()
        await dst.close()