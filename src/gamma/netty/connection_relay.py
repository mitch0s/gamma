import asyncio
import logging
import time
from gamma.netty.connection import Connection
from gamma.netty.player_connection import PlayerConnection, PlayerConnectionType
from gamma.netty.server_connection import ServerConnection
from gamma.packet.player_handshake_handler import PlayerHandshakePacketHandler
from gamma.response.invalid_hostname_motd import invalid_hostname_motd
from gamma.response.invalid_hostname_disconnect import invalid_hostname_disconnect

logger = logging.getLogger()


class ConnectionRelay:
    def __init__(self, id: int, downstream: PlayerConnection, upstream: ServerConnection):
        self.id = id
        self.created_ts = time.time()
        self.downstream = downstream
        self.upstream = upstream
        self.total_packets = 0
        self.total_bytes = 0
        self._connection_open = True
        self._last_bandwidth = 0

    async def start(self):
        logger.debug('Connection opened.')

        # attach handshake parser
        PlayerHandshakePacketHandler(self.downstream)

        try:
            await self._handshake_then_relay()
        except Exception as e:
            logger.debug(str(e))
        finally:
            await self.downstream.close()
            await self.upstream.close()

            logger.debug('Connection closed.')
            if self.downstream.type == PlayerConnectionType.PLAY:
                logger.info(
                    f'{self.downstream.username} '
                    f'({self.downstream.host_addr}:{self.downstream.host_port}) '
                    f'LEFT {self.downstream.hostname}'
                )
            self._connection_open = False
            del self

    async def _handshake_then_relay(self):
        await self.downstream.start()

        buffer = bytearray()

        # read + buffer until handshake resolved
        while True:
            data = await self.downstream.reader.read(8192)
            if not data:
                raise EOFError()

            buffer += data

            # let handler inspect (no copy ideally)
            if self.downstream._packet_handlers:
                self.downstream._handle_packet(data)

            if self.downstream.type and self.downstream.hostname:
                break

        # handle invalid hostname
        if self.downstream.hostname == 'localhost':
            if self.downstream.type == PlayerConnectionType.PING:
                logger.info(
                    f'Player ({self.downstream.host_addr}:{self.downstream.host_port}) '
                    f'PINGED INVALID HOSTNAME: {self.downstream.hostname}'
                )
                self.downstream.writer.write(invalid_hostname_motd())

            if self.downstream.type == PlayerConnectionType.PLAY:
                logger.info(
                    f'Player ({self.downstream.host_addr}:{self.downstream.host_port}) '
                    f'JOINED INVALID HOSTNAME: {self.downstream.hostname}'
                )
                self.downstream.writer.write(invalid_hostname_disconnect())

            await self.downstream.writer.drain()
            return

        # logging
        if self.downstream.type == PlayerConnectionType.PING:
            logger.info(
                f'Player ({self.downstream.host_addr}:{self.downstream.host_port}) '
                f'PINGED {self.downstream.hostname}'
            )

        if self.downstream.type == PlayerConnectionType.PLAY:
            logger.info(
                f'{self.downstream.username} '
                f'({self.downstream.host_addr}:{self.downstream.host_port}) '
                f'JOINED {self.downstream.hostname}'
            )

        # connect upstream
        await self.upstream.start()

        # flush buffered handshake to upstream
        self.upstream.writer.write(buffer)
        await self.upstream.writer.drain()

        # disable handlers (critical for performance)
        self.downstream._packet_handlers.clear()

        # Raw forwarding (FAST PATH)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._forward_raw(self.downstream, self.upstream))
            tg.create_task(self._forward_raw(self.upstream, self.downstream))

    async def _forward_raw(self, src: Connection, dst: Connection):
        try:
            while True:
                data = await src.reader.read(65536)
                if not data:
                    break

                dst.writer.write(data)

                self.total_bytes += len(data)
                self.total_packets += 1

                # small batching window
                await dst.writer.drain()

        except Exception:
            pass