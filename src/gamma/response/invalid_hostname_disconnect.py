from gamma.util.format.colour_codes import format_colour_codes
from gamma.util.bitwise.varint import varint


def invalid_hostname_disconnect():
    message = 'Disconnect Message'
    message = format_colour_codes(data=message).encode()
    message = b'{"extra":[{"text":"' + message + b'"}],"text":""}'
    packet_data_length_varint = varint(len(message))
    packet_length_varint = varint(len(message + packet_data_length_varint + b'\x00'))
    message = packet_length_varint + b'\x00' + packet_data_length_varint + message

    return message