class Packet:
    def __init__(self, id: int, data: bytes, raw: bytes = None):
        self.id = id
        self.data = data    # payload only (no length prefix)
        self.raw = raw      # original framed bytes (length prefix + payload)

