import asyncio
from asyncio import StreamReader, StreamWriter
from gamma.net.connection import Connection


class PlayerConnection(Connection):
    def __init__(self, reader:StreamReader=None, writer:StreamWriter=None):
        super().__init__(reader=reader, writer=writer)        