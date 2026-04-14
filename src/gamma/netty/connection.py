import logging
import asyncio
from asyncio import StreamReader, StreamWriter
from gamma.packet import Packet, PacketHandler
import time

logger = logging.getLogger()

class Connection:
    def __init__(self, reader:StreamReader, writer:StreamWriter):
        self.host_addr = None
        self.host_port = None
        self.reader = reader
        self.writer = writer
        self._read_queue: asyncio.Queue = asyncio.Queue()
        self._write_queue: asyncio.Queue = asyncio.Queue()
        self._packet_handlers: list[PacketHandler] = []
        self.packet_count = 0
        self.packet_bytes = 0
        self._last_write_flush = time.monotonic()

    def add_packet_handler(self, handler: PacketHandler):
        if handler:
            self._packet_handlers.append(handler)

    async def start(self):
        try: 
            peer_info = self.writer.get_extra_info('peername')
            self.host_addr, self.host_port = peer_info[:2]
        except Exception as error: 
            logger.error(error)

    async def close(self) -> None:
        if self.writer:
            self.writer.close()

    async def read(self) -> bytes|None:
        data = await self.reader.read(8192)
        if not data:
            raise EOFError('socket not available to read from')
        self.packet_bytes += len(data)
        self.packet_count += 1
        return self._handle_packet(data)

    async def write(self, packet:bytes) -> int:
        now = time.monotonic()
        self.writer.write(packet)
        self.packet_bytes += len(packet)
        self.packet_count += 1
        if now - self._last_write_flush > 0.05:
            await self.writer.drain()
            self._last_write_flush = now
        return len(packet)

    def _handle_packet(self, packet:bytes|None) -> bytes|None:
        for handler in self._packet_handlers:
            if packet is None:
                break
            packet = handler.handle(packet)
        return packet