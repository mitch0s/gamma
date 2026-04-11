import asyncio
import logging
from gamma.netty.connection import Connection
import time

logger = logging.getLogger()


class ConnectionRelay:
    def __init__(self, downstream:Connection=None, upstream:Connection=None):
        self.downstream = downstream
        self.upstream = upstream
        # session metrics
        self.total_packets = 0
        self.total_bytes = 0

    async def start(self):
        logger.info('Connection opened.')
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.downstream.start())
                tg.create_task(self.upstream.start())
                tg.create_task(self._forward(self.downstream, self.upstream))
                tg.create_task(self._forward(self.upstream, self.downstream))
        except Exception as error:
            print(error)
        await self.downstream.close()
        await self.upstream.close()
        logger.info('Connection closed.')

    async def _forward(self, src: Connection, dst: Connection):
        try:
            while True:
                data = await src.read()
                if not data:
                    break
                await dst.write(data)
                self.total_packets += 1
                self.total_bytes += len(data)
        finally:
            await src.close()   # unblocks src._read_loop and src._write_loop
            await dst.close()   # unblocks dst._read_loop and dst._write_loop