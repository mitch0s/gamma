import json

def varint(integer: int) -> bytes:
    """Encodes an integer as an uvarint.
    :param integer: the integer to encode
    :return: bytes containing the integer encoded as an uvarint
    """
    def to_byte(integer: int) -> int:
        return integer & 0b1111_1111

    buffer: bytearray = bytearray()

    while integer >= 0b1000_0000:
        buffer.append(to_byte(integer) | 0b1000_0000)
        integer >>= 7

    buffer.append(to_byte(integer))

    return bytes(buffer)

def server_offline_disconnect():
    # Reads settings file and ensures it's closed
    settings_file = open('./settings.json', 'r+')
    settings = json.loads(settings_file.read())
    settings_file.close()

    message = settings['messages']['server_offline']['disconnect_message'].encode()

    message = b'{"extra":[{"text":"' +message + b'"}],"text":""}'

    packet_data_length_varint = varint(len(message))

    packet_length_varint = varint(len(message + packet_data_length_varint + b'\x00'))


    message = packet_length_varint + b'\x00' + packet_data_length_varint + message

    return message