def get_conn_type(data):
    # Detect Connection Type
    conn_type = 'UNKNOWN'
    if b'\xdd\x02' in data:
        conn_type = 'PLAY'
    if b'\xdd\x01' in data:
        conn_type = 'PING'

    return conn_type
