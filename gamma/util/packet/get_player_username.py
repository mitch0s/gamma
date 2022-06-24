def get_player_username(data):
    try:
        legal_username_chars = 'abcdefghijklmnopqrstuvwxyzABCDEFFGHIJKLMNOPQRSTUVWXYZ1234567890_'

        if b'\xbc\x06\x00\x07' in data: # 1.19.X
            data = data[4:].split(b'\x01\x00\x00\x01')
            data = data[0]
            return data.decode()

        else: # All other protocols
            data = data.replace(b'\t\x00\x07', b'')
            username = data.decode()

            return username

    except IndexError:
        return None