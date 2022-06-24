import traceback

def get_conn_hostname(data):
    try:
        data = data[4:]
        data = data.split(b'c\xdd')

        hostname = ''
        for char in data[0]:
            char = chr(char)
            if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.":
                hostname += char

        hostname = hostname.replace('MCPingHost', '')

        return hostname

    except:
        traceback.print_exc()
        return None