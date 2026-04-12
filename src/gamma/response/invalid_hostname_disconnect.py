import json
from gamma.util.format.colour_codes import format_colour_codes
from gamma.util.bitwise.varint import varint


DEFAULT_MESSAGE = '&7&m------------------------------------------------------------------&r\n\n\n&d&lInvalid Hostname\n\n\n\n&r&8This hostname is not configured on the &5&lGamma Network&r\n\n\n&7&m------------------------------------------------------------------&r'

def invalid_hostname_disconnect():
    with open('./config.json', 'r+') as file:
        config = json.loads(file.read())
        file.close()

    cfg = config.get('invalid_hostname', {})
    message = format_colour_codes(cfg.get('disconnect', DEFAULT_MESSAGE)).encode()

    message = b'{"extra":[{"text":"' + message + b'"}],"text":""}'
    packet_data_length_varint = varint(len(message))
    packet_length_varint = varint(len(message + packet_data_length_varint + b'\x00'))
    message = packet_length_varint + b'\x00' + packet_data_length_varint + message

    return message