"""
./gamma/listen.py
"""
import socket
from .connection import Connection
import threading
import time


class Listen:
    def __init__(self, listen_addr, listen_port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen:
            listen.bind((listen_addr, listen_port))
            listen.listen()
            print(f'[?] Proxy listening on: {listen_addr}:{listen_port}')

            while True:
                downstream_conn, downstream_addr = listen.accept()
                threading.Thread(target=Connection, kwargs={'downstream_conn': downstream_conn, 'downstream_addr': downstream_addr}).start()
