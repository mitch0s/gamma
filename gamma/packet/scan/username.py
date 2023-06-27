def username(data:bytes):
    """
     Extract player username from an intercepted packet
    """

    # Versions: 1.12.2
    if b'\x06\x00\x04' in data:
        username = str(data.replace(b'\x06\x00\x04', b'').decode().strip())
        return username
