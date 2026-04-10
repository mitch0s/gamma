def hostname(data:bytes):
    """
     Extract hostname from an intercepted packet
    """
    hostname = None

    # Versions: 1.12.2
    if b'\x10\x00\xd4\x02\t' in data:
        hostname = data.replace(b'\x10\x00\xd4\x02\t', b'').replace(b'c\xdc\x01', b'').replace(b'c\xdc\x02', b'').decode().strip()

    # Versions: 1.12.2
    if b'\x0e\x00\xd4\x02\x07' in data:
        hostname = data.replace(b'\x0e\x00\xd4\x02\x07', b'').replace(b'c\xdc\x01', b'').replace(b'c\xdc\x02', b'').decode().strip()

    return hostname