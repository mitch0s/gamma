import base64
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


def invalid_hostname_motd():
    # Reads settings file and ensures it's closed
    settings_file = open('./settings.json', 'r+')
    settings = json.loads(settings_file.read())
    settings_file.close()

    # Read and Encode Data from settings
    version = settings['messages']['invalid_hostname']['version'].encode()
    motd = settings['messages']['invalid_hostname']['motd'].encode()

    # Open and Base64 encode the server icon
    with open(settings['messages']['invalid_hostname']['icon_path'], 'rb') as image:
        image = base64.b64encode(image.read())
        image = image.replace(b'=', b'')

    # Format the string to be sent in the response packet
    string = b'{"version":{"name":"' + version + b'","protocol":-1},"players":{"max":0,"online":0,"sample":null},"description":{"text":"' + motd + b'"},"favicon":"data:image/png;base64,'+image+b'"}'

    # Retrieves VARINT values for length of JSON
    # string and PACKET
    string_len_varint = varint(len(string))
    packet_len_varint = varint(len(string) + 3)

    # Combines everything together into a single bytearray
    message = packet_len_varint + b'\x00' + string_len_varint + string

    return message