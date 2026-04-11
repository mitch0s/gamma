import json
import base64
from gamma.util.format.colour_codes import format_colour_codes
from gamma.util.bitwise.varint import varint

def invalid_hostname_motd():

    with open('./config.json', 'r+') as file:
        config = json.loads(file.read())
        file.close()

    cfg = config.get('invalid_hostname', {})

    version = format_colour_codes(cfg.get('version', 'Gamma')).encode()
    motd = format_colour_codes(cfg.get('motd', 'Invalid hostname. Please check our documentation.')).encode()
    icon = cfg.get('icon', None)

    packet = b'{"version":{"name":"' + version + b'","protocol":-1},' \
             b'"players":{"max":0,"online":0,"sample":[]},' \
             b'"description":{"text":"' + motd + b'"}}'

    if icon:
        with open(icon, 'rb') as image:
            image = base64.b64encode(image.read())
            packet = b'{"version":{"name":"' + version + b'","protocol":-1},' \
                    b'"players":{"max":0,"online":0,"sample":[]},' \
                    b'"description":{"text":"' + motd + b'"},' \
                    b'"favicon":"data:image/png;base64,' + image + b'"}'

    string_len = varint(len(packet))
    packet_id = b'\x00'
    data = packet_id + string_len + packet
    packet_len = varint(len(data))
    return packet_len + data
