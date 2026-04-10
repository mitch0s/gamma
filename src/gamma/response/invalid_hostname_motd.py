import base64
import gamma as gamma

def invalid_hostname_motd():
    version = gamma.util.format.colour_codes(
        gamma.variable.invalid_hostname_motd_version
    ).encode()

    motd = gamma.util.format.colour_codes(
        gamma.variable.invalid_hostname_motd_text
    ).encode()

    packet = b'{"version":{"name":"' + version + b'","protocol":-1},' \
             b'"players":{"max":0,"online":0,"sample":[]},' \
             b'"description":{"text":"' + motd + b'"}}'

    if gamma.variable.invalid_hostname_motd_icon:
        with open(gamma.variable.invalid_hostname_motd_icon, 'rb') as image:
            image = base64.b64encode(image.read())
        packet = b'{"version":{"name":"' + version + b'","protocol":-1},' \
                 b'"players":{"max":69,"online":69,"sample":[]},' \
                 b'"description":{"text":"' + motd + b'"},' \
                 b'"favicon":"data:image/png;base64,' + image + b'"}'

    string_len = gamma.varint(len(packet))

    packet_id = b'\x00'
    data = packet_id + string_len + packet

    packet_len = gamma.varint(len(data))

    return packet_len + data