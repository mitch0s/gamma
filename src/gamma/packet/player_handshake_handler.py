import logging
import asyncio
from gamma.packet import Packet, PacketHandler
from gamma.netty.player_connection import PlayerConnection, PlayerConnectionType
from gamma.response.invalid_hostname_motd import invalid_hostname_motd

logger = logging.getLogger()


def _parse_varint(data: bytes, offset: int) -> tuple[int, int]:
    result = 0
    shift = 0
    while True:
        byte = data[offset]
        offset += 1
        result |= (byte & 0x7F) << shift
        if not (byte & 0x80):
            break
        shift += 7
    return result, offset


def _parse_string(data: bytes, offset: int) -> tuple[str, int]:
    length, offset = _parse_varint(data, offset)
    value = data[offset:offset + length].decode('utf-8', errors='ignore')
    return value, offset + length


def _iter_mc_packets(data: bytes):
    """
    Iterate over raw Minecraft packets in a data chunk.
    Yields (mc_packet_id, payload) where payload does NOT include the outer length varint.
    Handles multiple concatenated packets in a single read() call.
    """
    offset = 0
    while offset < len(data):
        try:
            length, offset = _parse_varint(data, offset)
            if offset + length > len(data):
                break
            payload = data[offset:offset + length]
            mc_packet_id, _ = _parse_varint(payload, 0)
            offset += length
            yield mc_packet_id, payload
        except (IndexError, UnicodeDecodeError):
            break


class PlayerHandshakePacketHandler(PacketHandler):
    """
    Parses Minecraft handshake and login packets to extract
    connection type, hostname, and username from the player connection.
    Disables itself once the handshake sequence is complete.
    """

    def __init__(self, connection: PlayerConnection):
        super().__init__(connection)
        self.connection = connection
        self._done = False

    def handle(self, packet: Packet) -> Packet:
        if self._done:
            return packet
        try:
            for mc_id, payload in _iter_mc_packets(packet.data):
                if self._done:
                    break

                if mc_id == 0x00 and self.connection.type is None:
                    self._parse_handshake(payload)

                elif mc_id == 0x00 and self.connection.type == PlayerConnectionType.PLAY:
                    self._parse_login(payload)
                    self._done = True

        except Exception as e:
            logger.debug('HandshakePacketHandler error on packet id=%d: %s', packet.id, e)

        return packet

    def _parse_handshake(self, data: bytes):
        print(f'_parse_handshake called, data={data[:20].hex()}')
        offset = 0
        _packet_id, offset = _parse_varint(data, offset)
        _protocol, offset = _parse_varint(data, offset)
        hostname, offset = _parse_string(data, offset)
        _port = int.from_bytes(data[offset:offset + 2], 'big')
        offset += 2
        next_state, _ = _parse_varint(data, offset)

        self.connection.hostname = hostname
        self.connection.type = (
            PlayerConnectionType.PING if next_state == 1
            else PlayerConnectionType.PLAY
        )

        logger.debug('Handshake: type=%s hostname=%s protocol=%d',
                     self.connection.type, self.connection.hostname, _protocol)

    def _parse_login(self, data: bytes):
        # payload has no outer length prefix
        offset = 0
        _packet_id, offset = _parse_varint(data, offset)
        username, _ = _parse_string(data, offset)
        self.connection.username = username
        logger.debug('Login Start: username=%s', self.connection.username)