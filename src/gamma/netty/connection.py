import logging
import asyncio
from asyncio import StreamReader, StreamWriter
from gamma.packet import Packet, PacketHandler
import traceback

logger = logging.getLogger()

_SENTINEL = object()


class Connection:
    def __init__(self, reader:StreamReader, writer:StreamWriter):
        # connection interfaces / buffers
        self.reader = reader
        self.writer = writer
        self._read_queue: asyncio.Queue = asyncio.Queue()
        self._write_queue: asyncio.Queue = asyncio.Queue()
        self._packet_handlers:list[PacketHandler] = []
        # state tracking
        self.packet_count = 0
        self.packet_bytes = 0

    def add_packet_handler(self, handler:PacketHandler):
        """
        add a packet handler to packet handler list
        """
        if handler:
            self._packet_handlers.append(handler)

    async def start(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._read_loop())
            tg.create_task(self._write_loop())

    async def close(self) -> None:
        await self._write_queue.put(Packet(id=-1, data=_SENTINEL))
        await self._read_queue.put(Packet(id=-1, data=_SENTINEL))
        if self.writer is None:
            return
        try:
            await self.writer.drain()
            self.writer.close()
            await self.writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError, EOFError, RuntimeError):
            pass

    async def read(self) -> Packet|None:
        packet:Packet = await self._read_queue.get()
        if packet.data is _SENTINEL:
            return None
        return packet

    def read_nowait(self) -> Packet|None:
        try:
            packet:Packet = self._read_queue.get_nowait()
            return None if packet.data is _SENTINEL else packet
        except asyncio.QueueEmpty:
            return None

    async def write(self, packet:Packet) -> int:
        if not packet:
            return 0
        await self._write_queue.put(packet)
        return len(packet.data)

    async def _read_loop(self):
        packet_id = 0
        try:
            while True:
                data = await self.reader.read(256)
                if not data:
                    break
                packet = await self._handle_packet(Packet(id=packet_id, data=data))
                if packet:
                    await self._read_queue.put(packet)
                    self.packet_bytes += len(data)
                    self.packet_count += 1
                    packet_id += 1
        except (asyncio.IncompleteReadError, ConnectionResetError, EOFError):
            pass
        except asyncio.CancelledError:
            pass
        finally:
            await self._read_queue.put(Packet(id=-1, data=_SENTINEL))

    async def _write_loop(self):
        try:
            while True:
                packet: Packet = await self._write_queue.get()
                if packet.data is _SENTINEL:
                    break
                self.writer.write(packet.data)
                # only drain if queue is empty — batch writes when busy
                if self._write_queue.empty():
                    await self.writer.drain()
                self.packet_bytes += len(packet.data)
                self.packet_count += 1
        except (ConnectionResetError, BrokenPipeError, EOFError):
            pass
        except asyncio.CancelledError:
            pass

    async def _handle_packet(self, packet:Packet|None) -> Packet|None:
        for handler in self._packet_handlers:
            if packet == None : break
            packet = handler.handle(packet) 
        return packet
