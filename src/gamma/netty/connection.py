import logging
import asyncio
from asyncio import StreamReader, StreamWriter

logger = logging.getLogger()

_SENTINEL = object()


class Connection:
    def __init__(self, reader: StreamReader = None, writer: StreamWriter = None):
        self.reader = reader
        self.writer = writer

        self._read_queue: asyncio.Queue = asyncio.Queue()
        self._write_queue: asyncio.Queue = asyncio.Queue()

        self.packet_recv_count = 0
        self.packet_recv_bytes = 0
        self.packet_sent_count = 0
        self.packet_sent_bytes = 0

    async def start(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._read_loop())
            tg.create_task(self._write_loop())

    async def close(self) -> None:
        await self._write_queue.put(_SENTINEL)
        await self._read_queue.put(_SENTINEL)
        try:
            await self.writer.drain()
            self.writer.close()
            await self.writer.wait_closed()
        except (ConnectionResetError, BrokenPipeError, EOFError, RuntimeError):
            pass

    async def read(self) -> bytes | None:
        data = await self._read_queue.get()
        if data is _SENTINEL:
            return None
        return data

    def read_nowait(self) -> bytes | None:
        try:
            data = self._read_queue.get_nowait()
            return None if data is _SENTINEL else data
        except asyncio.QueueEmpty:
            return None

    async def write(self, data: bytes) -> int:
        if not data:
            return 0
        await self._write_queue.put(data)
        return len(data)

    async def _read_loop(self):
        try:
            while True:
                data = await self.reader.read(1024)
                if not data:
                    break
                await self._read_queue.put(data)
                self.packet_recv_bytes += len(data)
                self.packet_recv_count += 1
        except (asyncio.IncompleteReadError, ConnectionResetError, EOFError):
            pass
        except asyncio.CancelledError:
            pass
        finally:
            await self._read_queue.put(_SENTINEL)

    async def _write_loop(self):
        try:
            while True:
                data = await self._write_queue.get()
                if data is _SENTINEL:
                    break
                self.writer.write(data)
                await self.writer.drain()
                self.packet_sent_bytes += len(data)
                self.packet_sent_count += 1
        except (ConnectionResetError, BrokenPipeError, EOFError):
            pass
        except asyncio.CancelledError:
            pass  # <-- this was missing
