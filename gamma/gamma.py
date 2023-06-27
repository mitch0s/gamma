import socket
import time
import gamma


class Gamma:
    debug:bool = False
    config:dict = {}
    socket: socket.socket
    event_func:list = []

    def bind(self, host:str='localhost', port:int=25565):
        """
         Create the TCP Socket Server.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.debug : print('[DEBUG] Created socket server')
        if self.debug: print(f'[DEBUG] Attempting to bind to port ({host}:{port})')
        while True:
            try:
                self.socket.bind((host, port))
                break

            except:
                time.sleep(0.2)
        if self.debug: print(f'[DEBUG] Successfully bound to port ({host}:{port})')


    def listen(self):
        """
         Start accepting player connections.
        """
        self.socket.listen()
        if self.debug: print(f'[DEBUG] Socket server listening')
        while True:
            downstream_conn, downstream_addr = self.socket.accept()
            if downstream_conn:
                gamma.Connection(downstream_conn=downstream_conn, downstream_addr=downstream_addr)
