import base64
import gamma

def server_offline_motd():
    # Read and Encode Data from settings
    version = gamma.variable.offline_motd_version
    motd = gamma.variable.offline_motd_text

    # Format the config data
    version = gamma.util.format.colour_codes(data=version).encode()
    motd = gamma.util.format.colour_codes(data=motd).encode()

    # Open and Base64 encode the server icon
    packet = b'{"version":{"name":"' + version + b'","protocol":-1},"players":{"max":0,"online":0,"sample":null},"description":{"text":"' + motd + b'"}}'
    if gamma.variable.offline_motd_icon:
        with open(gamma.variable.offline_motd_icon, 'rb') as image:
            image = base64.b64encode(image.read())
            image = image.replace(b'=', b'')
        packet = b'{"version":{"name":"' + version + b'","protocol":-1},"players":{"max":0,"online":0,"sample":null},"description":{"text":"' + motd + b'"}, "favicon":"data:image/png;base64,' + image + b'"}'


    # Retrieves VARINT values for length of JSON
    # string and PACKET
    string_len_varint = gamma.varint(len(packet))
    packet_len_varint = gamma.varint(len(packet) + 3)

    # Combines everything together into a single bytearray
    packet = packet_len_varint + b'\x00' + string_len_varint + packet

    return packet