
def varint(value):
        varint = bytearray()
        while True:
            b = value & 0x7F
            value >>= 7
            if value:
                varint.append(b | 0x80)
            else:
                varint.append(b)
                break
        return bytes(varint)