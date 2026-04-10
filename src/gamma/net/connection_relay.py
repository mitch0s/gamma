import asyncio
from gamma.net.connection import Connection
import time


class ConnectionRelay:
    def __init__(self, downstream:Connection=None, upstream:Connection=None):
        self.downstream = downstream
        self.upstream = upstream
        self._last_output = time.time()

        self.total_packets = 0
        self.total_bytes = 0

    async def start(self):
        """
        contunuously forward packets between clients
        """
        try:
            async with asyncio.TaskGroup() as tg:
                tg.create_task(self.downstream.start())
                tg.create_task(self.upstream.start())
                tg.create_task(self._relay_loop())
        except Exception as error:
            print(error)

    async def _relay_loop(self):
        while True:
            await asyncio.sleep(0)
            # forward DOWNSTREAM --> UPSTREAM
            ds_packet = self.downstream.read()
            if ds_packet :
                self.upstream.write(ds_packet)
            # forward UPSTREAM --> DOWNSTREAM
            us_packet = self.upstream.read()
            if us_packet: 
                self.downstream.write(us_packet)
            # print stats if required
            now = time.time()
            if now - self._last_output > 0.1:
                self._last_output = now
                



