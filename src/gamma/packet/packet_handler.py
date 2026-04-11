from gamma.packet import Packet


class PacketHandler:
    def __init__(self, connection):
        connection.add_packet_handler(self)
        self.connection = connection

    async def handle(self, packet: Packet = None) -> Packet:
        raise NotImplementedError('this method was not abstracted by a subclass')