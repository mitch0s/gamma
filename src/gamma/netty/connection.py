import logging
import asyncio
from asyncio import StreamReader, StreamWriter
from gamma.packet import Packet, PacketHandler
import traceback

logger = logging.getLogger()

class Connection:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader = reader
        self.writer = writer
        self._read_queue: asyncio.Queue = asyncio.Queue()
        self._write_queue: asyncio.Queue = asyncio.Queue()
        self._packet_handlers: list[PacketHandler] = []
        self.packet_count = 0
        self.packet_bytes = 0

    def add_packet_handler(self, handler: PacketHandler):
        if handler:
            self._packet_handlers.append(handler)

    async def start(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._read_loop())
            tg.create_task(self._write_loop())

    async def close(self) -> None:
        if self.writer:
            self.writer.close()

    async def read(self) -> Packet|None:
        return await self._read_queue.get()

    async def write(self, packet:Packet) -> int:
        if not packet.data:
            raise Exception()
        await self._write_queue.put(packet)
        return len(packet.data)

    async def _read_loop(self):
        packet_id = 0
        while True:
            data = await self.reader.read(256)
            if not data:
                raise EOFError('socket not available to read from')
            packet = self._handle_packet(Packet(id=packet_id, data=data))
            if packet:
                await self._read_queue.put(packet)
                self.packet_bytes += len(data)
                self.packet_count += 1
                packet_id += 1

    async def _write_loop(self):
        while True:
            packet: Packet = await self._write_queue.get()
            self.writer.write(packet.data)
            if self._write_queue.empty():
                await self.writer.drain()
            self.packet_bytes += len(packet.data)
            self.packet_count += 1

    def _handle_packet(self, packet: Packet | None) -> Packet | None:
        for handler in self._packet_handlers:
            if packet is None:
                break
            packet = handler.handle(packet)
        return packet