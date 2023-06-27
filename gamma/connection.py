import socket
import sys
import threading
import time
import gamma


class Connection:
    """
     This class defines how the proxy handles proxied data.
    """
    conn_alive = True
    conn_type = None
    found_username = False
    found_hostname = False

    # socket.socket objects
    upstream_conn:socket.socket = None
    downstream_conn:socket.socket = None

    # IPv4 addresses
    downstream_addr:tuple = ()  # IP:PORT of player
    upstream_addr:tuple = ()  # IP:PORT of server

    downstream_connect_hostname:str = None  # Hostname used to connect to server

    # Miscellaneous player info
    player_username:str = None
    player_version:str = None

    downstream_bandwidth:int = 0
    upstream_bandwidth:int = 0

    downstream_timeout:int = 3
    upstream_timeout:int = 3

    downstream_epoch:float = 0
    upstream_epoch:float = 0


    def __init__(self, downstream_conn, downstream_addr:tuple) -> None:
        self.downstream_conn = downstream_conn
        self.downstream_addr = downstream_addr
        threading.Thread(target=self.setup_streams).start()

    def setup_streams(self) -> None:
        """
         Connect to upstream, once connected, start relaying packets.
        """
        # Extract information from initial downstream packets.
        self.downstream_packet_backlog = []
        while True:
            data = self.downstream_conn.recv(2048)
            gamma.event.call.downstream_packet(data=data, PlayerConnection=self)
            if not self.downstream_connect_hostname : self.downstream_connect_hostname = gamma.packet.scan.hostname(data=data)
            if not self.conn_type : self.conn_type = gamma.packet.scan.connection_type(data=data)
            if not self.player_username : self.player_username = gamma.packet.scan.username(data=data)
            self.downstream_packet_backlog.append(data)

            if self.conn_type == 'PING' and self.downstream_connect_hostname is not None:
                break
            if self.conn_type == 'PLAY' and self.downstream_connect_hostname is not None and self.player_username is not None:
                break


        # Attempt a connection to upstream server
        try:
            self.netconfig = gamma.util.fetch.hostname_config(hostname=self.downstream_connect_hostname)
            if not self.netconfig:
                if self.conn_type == 'PING' : self.downstream_conn.send(gamma.response.invalid_hostname_motd())
                if self.conn_type == 'PLAY' : self.downstream_conn.send(gamma.response.invalid_hostname_disconnect())
                sys.exit()

            self.upstream_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.upstream_conn.connect((self.netconfig['backend_ip'], self.netconfig['backend_port']))

        # Catch offline exception, return offline MOTD response
        except ConnectionRefusedError:
            match self.conn_type:
                case 'PING' : self.downstream_conn.send(gamma.response.server_offline_motd())
                case 'PLAY': self.downstream_conn.send(gamma.response.server_offline_disconnect())

        self.upstream_epoch = time.time()
        self.downstream_epoch = time.time()

        threading.Thread(target=self.handle_upstream_packet).start()
        threading.Thread(target=self.handle_downstream_packet).start()
        sys.exit()


    def handle_downstream_packet(self) -> None:
        """
         Handle all data received from the downstream connection (Player)
        """
        gamma.event.call.downstream_connect(PlayerConnection=self)
        while self.conn_alive:
            try:
                data = self.downstream_conn.recv(2048)
                if data:
                    self.downstream_bandwidth += len(data)
                    data = gamma.event.call.downstream_packet(data=data, PlayerConnection=self)
                    if self.upstream_conn : self.upstream_conn.send(data)

            except (ConnectionResetError, BrokenPipeError, OSError):
                self.conn_alive = False


        sys.exit()



    def handle_upstream_packet(self) -> None:
        """
         Handle all data received from the upstream connection (Server)
        """
        # Send packet backlog to upstream connection
        for packet in self.downstream_packet_backlog:
            if self.netconfig['proxy_protocol']:
                if self.downstream_packet_backlog.index(packet) == 0:
                    packet = b'PROXY TCP4 ' + self.downstream_addr[0].encode() + b' 255.255.255.255 ' + str(self.downstream_addr[1]).encode() + b' 25565\r\n' + packet
            self.upstream_conn.send(packet)

        gamma.event.call.upstream_connect(PlayerConnection=self)
        while self.conn_alive:
            data = self.upstream_conn.recv(2048)
            if data:
                data = gamma.event.call.upstream_packet(data=data, PlayerConnection=self)

                try:
                    self.upstream_bandwidth += len(data)
                    if self.downstream_conn: self.downstream_conn.send(data)


                except (ConnectionResetError, BrokenPipeError, OSError):
                    self.conn_alive = False

        gamma.event.call.upstream_disconnect(PlayerConnection=self)
        sys.exit()

    def exit(self):
        if self.upstream_conn : self.upstream_conn.close()
        if self.downstream_conn : self.downstream_conn.close()
