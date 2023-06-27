import gamma

def invalid_hostname_disconnect():
    message = gamma.variable.invalid_hostname_disconnect_text
    message = gamma.util.format.colour_codes(data=message).encode()
    message = b'{"extra":[{"text":"' + message + b'"}],"text":""}'
    packet_data_length_varint = gamma.util.varint(len(message))
    packet_length_varint = gamma.util.varint(len(message + packet_data_length_varint + b'\x00'))
    message = packet_length_varint + b'\x00' + packet_data_length_varint + message

    return message