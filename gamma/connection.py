import socket
import sys
import threading
import time
import gamma


class Connection:
    """
     This class defines how the proxy handles proxied data.
    """
    conn_alive = True  # Both sides of the connection are open + healthy
    conn_type = None  # Connection type -> PLAY or PING

    # socket.socket objects
    upstream_conn:socket.socket = None
    downstream_conn:socket.socket = None

    # IPv4 addresses
    downstream_addr:tuple = ()  # IP:PORT of player
    upstream_addr:tuple = ()  # IP:PORT of server

    downstream_connect_hostname:str = None  # Hostname used to connect to server

    # Miscellaneous player info
    player_username:str = None  # Username of player
    player_version:str = None  # NOT USED - Version of player's Minecraft client

    downstream_bandwidth:int = 0  # Total bandwidth received from downstream/player
    upstream_bandwidth:int = 0  # Total bandwidth received from upstream/server

    downstream_packet_count:int = 0  # Total amount of packets received from downstream/player
    upstream_packet_count:int = 0  # Total amount of packets received from upstream/server

    downstream_timeout:int = 3  # Downstream timeout duration
    upstream_timeout:int = 3  # Upstream timeout duration

    downstream_epoch:float = 0  # Ignore
    upstream_epoch:float = 0 # Ignore


    def __init__(self, downstream_conn, downstream_addr:tuple) -> None:
        """

        :param downstream_conn: socket.socket object that has a connection to downstream/player
        :param downstream_addr: ip:port tuple for the player
        """
        # Assigning arguments to class-wide variables
        self.downstream_conn = downstream_conn
        self.downstream_addr = downstream_addr
        # Start connection-setup on another thread- allows main to go continue searching for connections
        threading.Thread(target=self.setup_streams).start()

    def setup_streams(self) -> None:
        """
         Connect to upstream, once connected, start relaying packets.
        """
        # Keep backlog of packets received from downstream/player, but not forwarded to upstream/server
        self.downstream_packet_backlog = []
        while True:
            data = self.downstream_conn.recv(2048)  # Receive data from downstream/player
            data = gamma.event.call.downstream_packet(data=data, PlayerConnection=self)  # Pass packet to downstream_packet event/hook
            # Scan packet for connection hostname if not found already
            if not self.downstream_connect_hostname : self.downstream_connect_hostname = gamma.packet.scan.hostname(data=data)
            # Scan packet for connection type PING/PLAY if not found already
            if not self.conn_type : self.conn_type = gamma.packet.scan.connection_type(data=data)
            # Scan packet for player username if not found already
            if not self.player_username : self.player_username = gamma.packet.scan.username(data=data)
            # Add packet to downstream packet backlog, to be sent upstream l8r
            self.downstream_packet_backlog.append(data)

            # Conditions/data required for PING connection
            if self.conn_type == 'PING' and self.downstream_connect_hostname is not None:
                break

            # Conditions/data required for PLAY connection
            if self.conn_type == 'PLAY' and self.downstream_connect_hostname is not None and self.player_username is not None:
                break


        # Attempt a connection to upstream server
        try:
            # Fetch the config attributed to hostname
            self.netconfig = gamma.util.fetch.hostname_config(hostname=self.downstream_connect_hostname)
            # Send invalid hostname responses if config doesn't exist. Close connection.
            if not self.netconfig:
                if self.conn_type == 'PING' : self.downstream_conn.send(gamma.response.invalid_hostname_motd())
                if self.conn_type == 'PLAY' : self.downstream_conn.send(gamma.response.invalid_hostname_disconnect())
                sys.exit()

            # Connect to ip:port in config
            self.upstream_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.upstream_conn.connect((self.netconfig['backend_ip'], self.netconfig['backend_port']))

        # Catch offline exception, return offline MOTD response
        except ConnectionRefusedError:
            match self.conn_type:
                case 'PING' : self.downstream_conn.send(gamma.response.server_offline_motd())
                case 'PLAY': self.downstream_conn.send(gamma.response.server_offline_disconnect())

        # Start epochs since connected
        self.upstream_epoch = time.time()
        self.downstream_epoch = time.time()

        # Start upstream packet handler on another thread
        threading.Thread(target=self.handle_upstream_packet).start()
        # Use this thread to handle downstream packets
        self.handle_downstream_packet()


    def handle_downstream_packet(self) -> None:
        """
         Handle all data received from the downstream/player connection (Player)
        """
        # Call downstream connect event
        gamma.event.call.downstream_connect(PlayerConnection=self)
        while self.conn_alive:
            try:
                data = self.downstream_conn.recv(2048)  # Receive
                if data:
                    self.downstream_packet_count += 1
                    self.downstream_bandwidth += len(data)
                    data = gamma.event.call.downstream_packet(data=data, PlayerConnection=self)
                    self.upstream_conn.send(data)
            except (ConnectionResetError, BrokenPipeError, OSError):
                self.conn_alive = False
        sys.exit()



    def handle_upstream_packet(self) -> None:
        """
         Handle all data received from the upstream/server connection (Server)
        """
        # Send packet backlog to upstream connection
        for packet in self.downstream_packet_backlog:
            # Add proxy protocol v1 if enabled in config.
            if self.netconfig['proxy_protocol']:
                if self.downstream_packet_backlog.index(packet) == 0:
                    packet = b'PROXY TCP4 ' + self.downstream_addr[0].encode() + b' 255.255.255.255 ' + str(self.downstream_addr[1]).encode() + b' 25565\r\n' + packet
            self.upstream_conn.send(packet)

        gamma.event.call.upstream_connect(PlayerConnection=self)
        while self.conn_alive:
            try:
                data = self.upstream_conn.recv(2048)
                if data:
                    self.upstream_packet_count += 1
                    self.upstream_bandwidth += len(data)
                    data = gamma.event.call.upstream_packet(data=data, PlayerConnection=self)
                    self.downstream_conn.send(data)

            # Catch connection disconnect exceptions
            except (ConnectionResetError, BrokenPipeError, OSError):
                self.conn_alive = False

            # Close connection if open for more than timeout specifies, prevents gaping threads for Minecraft's 30s timeout
            # Otherwise people can abuse by spam-pinging, leaving hundreds of open threads, potentially crashing the proxy.
            if self.conn_type == 'PING' and time.time() - self.upstream_epoch > self.upstream_timeout:
                self.conn_alive = False

        gamma.event.call.upstream_disconnect(PlayerConnection=self)
        sys.exit()
