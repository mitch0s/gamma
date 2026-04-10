import asyncio
from asyncio import StreamReader, StreamWriter
from datetime import datetime, UTC

class Connection:
    def __init__(self, reader:StreamReader=None, writer:StreamWriter=None):
        self.reader = reader
        self.writer = writer

        self._read_queue:list[bytes] = []
        self._write_queue:list[bytes] = []
        
        # connection tracking
        self.packet_recv_count = 0
        self.packet_recv_bytes = 0
        self.packet_sent_count = 0
        self.packet_sent_bytes = 0

    async def start(self):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(self._read_loop())
            tg.create_task(self._write_loop())
            self.write()

    def close(self) -> None:
        """
        close the write connection. also collapses reader connection.
        """
        self.writer.close()

    def read(self) -> bytes|None:
        """
        read data from read queue.
        """
        if len(self._read_queue) > 0:
            return self._read_queue.pop(0)
        
    def write(self, data:bytes=None) -> int:
        """
        add data to write queue to be written later.
        """
        if not data : return
        self._write_queue.append(data)
        return len(data)

    async def _read_loop(self):
        """
        continuously append data read from socket to read queue.
        """
        while True:
            data = await self.reader.read(1024)
            if data:
                self._read_queue.append(data)
                self.packet_recv_bytes += len(data)
                self.packet_recv_count += 1
            await asyncio.sleep(0)

    async def _write_loop(self):
        """
        continuously write data to socket from write queue.
        """
        while True:
            if len(self._write_queue) > 0:
                data = self._write_queue.pop(0)
                self.writer.write(data)
                await self.writer.drain()
                self.packet_sent_bytes += len(data)
                self.packet_sent_count += 1
            await asyncio.sleep(0)