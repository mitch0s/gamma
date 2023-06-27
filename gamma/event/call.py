downstream_connect_func = []
upstream_connect_func = []
downstream_disconnect_func = []
upstream_disconnect_func = []
downstream_packet_func = []
upstream_packet_func = []

def downstream_connect(PlayerConnection=None):
    for func in downstream_connect_func:
        func(PlayerConnection)

def upstream_connect(data=b'', PlayerConnection=None):
    for func in upstream_connect_func:
        func(PlayerConnection)

def downstream_disconnect(PlayerConnection=None):
    for func in downstream_disconnect_func:
        func(PlayerConnection)

def upstream_disconnect(PlayerConnection=None):
    for func in upstream_disconnect_func:
            func(PlayerConnection)

def downstream_packet(data=b'', PlayerConnection=None):
    for func in downstream_packet_func:
        data = func(data, PlayerConnection)
    return data

def upstream_packet(data=b'', PlayerConnection=None):
    for func in upstream_packet_func:
        data = func(data, PlayerConnection)
    return data

