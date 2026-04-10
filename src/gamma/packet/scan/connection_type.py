def connection_type(data:bytes):
    """
     Extract connection type from an intercepted packet
    """
    connection = None

    # Versions: 1.12.2
    if b'c\xdc\x01' in data:
        connection = 'PING'

    # Versions: 1.12.2
    if b'c\xdc\x02' in data:
        connection = 'PLAY'

    return connection