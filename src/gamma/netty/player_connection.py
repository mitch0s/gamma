from asyncio import StreamReader, StreamWriter
from gamma.netty.connection import Connection
from enum import Enum, auto

class PlayerConnectionType(Enum):
    UNKNOWN = auto()
    PING    = auto()
    PLAY    = auto()

class PlayerConnection(Connection):
    def __init__(self, reader:StreamReader=None, writer:StreamWriter=None):
        super().__init__(reader=reader, writer=writer)     
        self.username:str = None  # username of connected client
        self.hostname:str = None  # hostname in handshake packet (used to route to specific backend)
        self.type:PlayerConnectionType = None