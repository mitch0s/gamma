import gamma


def downstream_connect(func):
    if func:
        gamma.event.call.downstream_connect_func.append(func)

def upstream_connect(func):
    if func:
        gamma.event.call.upstream_connect_func.append(func)

def downstream_disconnect(func):
    if func:
        gamma.event.call.downstream_disconnect_func.append(func)

def upstream_disconnect(func):
    if func:
        gamma.event.call.upstream_disconnect_func.append(func)

def downstream_packet(func):
    if func:
        gamma.event.call.downstream_packet_func.append(func)

def upstream_packet(func):
    if func:
        gamma.event.call.upstream_packet_func.append(func)

