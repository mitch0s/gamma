"""
./gamma/connection.py
"""
import sys
import threading
import traceback
from .util import *
import socket
import time

class Connection:
    def __init__(self, **kwargs):
        self.debug = False
        self.debug_settings = {
            'print_upstream': True,
            'print_downstream': True,
            'print_exceptions': True
        }

        # PROXY <---> SERVER connection
        self.upstream_conn = None # socket object for the CLIENT <---> PROXY connection
        self.downstream_conn = kwargs['downstream_conn'] # socket object for the CLIENT <---> PROXY connection


        # Global status to determine whether
        # the connection is active or not
        self.conn_alive = True

        # DATA RECORDED IN CONNECTION
        # Username of connected player
        self.player_username = None

        # Hostname requested by player
        self.conn_hostname = None

        # Total bandwidth used by connection
        self.conn_bandwidth = 0

        # Total upstream/downstream packets
        self.downstream_packet_count = 0
        self.upstream_packet_count = 0

        # Address, Port attributed to each connection
        self.downstream_address = kwargs['downstream_addr']
        self.upstream_address = (None, None, None)

        # MISC CHECKS
        self.found_player_username = False

        ##########################################################

        # Receives initial data from downstream connection
        data = self.downstream_conn.recv(8192)

        self.conn_type = packet.get_conn_type(data) # Gets the connection type: PING, PLAY or UNKNOWN

        # Finds hostname from within the first packet
        self.conn_hostname = packet.get_conn_hostname(data)

        # Gets backend (ip, port, proxy_protocol) for hostname
        self.upstream_address = server.get_server_backend(self.conn_hostname)

        # Appends the v1 proxy protocol schema if enabled
        if self.upstream_address[2] == True:
            data = b'PROXY TCP4 ' + self.downstream_address[0].encode() + b' 255.255.255.255 ' + str(self.downstream_address[1]).encode() + b' 25565\r\n' + data
        if self.debug and self.debug_settings['print_upstream']:
            print(data)

        # If the IP for hostname == None (Not found), return
        # invalid hostname motd to the downstream connection
        if self.upstream_address[0] is None and self.conn_type == 'PING':
            self.downstream_conn.send(message.invalid_hostname_motd())
            self.conn_alive = False
            self.on_invalid_hostname_ping()
            sys.exit()

        # Sends disconnect message if connection is `PLAY` and
        # no server config is found
        if self.upstream_address[0] is None and self.conn_type == 'PLAY':
            self.downstream_conn.send(message.invalid_hostname_disconnect())
            self.conn_alive = False
            sys.exit()

        threading.Thread(target=self.upstream).start()  # Starts a `PROXY <---> SERVER` thread

        threading.Thread(target=self.downstream, kwargs={'data': data}).start()  # Starts a `CLIENT <---> PROXY` thread

        sys.exit()



    def upstream(self, **kwargs):
        try:
            self.upstream_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.upstream_conn.settimeout(2)

            try:
                self.upstream_conn.connect((self.upstream_address[0], self.upstream_address[1]))
            except TimeoutError:
                if self.conn_type == 'PING':
                    self.downstream_conn.send(message.server_offline_motd())
                if self.conn_type == 'PLAY':
                    self.downstream_conn.send(message.server_offline_disconnect())

                self.conn_alive = False
                self.on_server_offline()

            self.upstream_conn_packets = 0

            while self.conn_alive:
                data = self.upstream_conn.recv(8192)

                if data:
                    if self.debug and self.debug_settings['print_upstream']:
                        print('[<]', data)

                    self.last_upstream_packet = time.time()

                    self.upstream_conn_packets += 1 # Adds 1 to upstream packet counter
                    self.conn_bandwidth += len(data) # Adds packet length to bandwidth counter

                    self.downstream_conn.send(data)

                # Breaks the connection if the last PING packet was more than 2 seconds ago
                if self.conn_type == 'PING' and time.time() - self.last_upstream_packet > 2:
                    self.on_ping()
                    self.conn_alive = False

            self.upstream_conn.close()  # Close the connection if self.conn_alive == False
            sys.exit()

        except Exception as error:
            self.conn_alive = False
            self.on_player_disconnect()

            if self.debug:
                traceback.print_exc()

            sys.exit()



    def downstream(self, **kwargs):
        """
        PLAYER <--> PROXY
        """
        time.sleep(0.5)

        try:

            if 'data' in kwargs:
                self.upstream_conn.send(kwargs['data'])

            while self.conn_alive:
                if self.conn_type == 'PING' and self.upstream_conn_packets >= 5:
                    self.on_ping()
                    self.conn_alive = False

                data = self.downstream_conn.recv(8192)

                if data:
                    if self.debug and self.debug_settings['print_downstream']:
                        print(f'[>]', data)

                    if self.downstream_packet_count == 0 and self.conn_type == 'PLAY':
                        self.player_username = packet.get_player_username(data)
                        self.on_player_connect()

                    self.downstream_packet_count += 1

                    self.conn_bandwidth += len(data) # Adds packet length to bandwidth counter

                    self.upstream_conn.send(data) # Relays the data received to the upstream conn (server)


            self.downstream_conn.close() # Close the connection if self.conn_alive == False
            sys.exit()

        except Exception as error:
            self.conn_alive = False

            if self.debug:
                traceback.print_exc()

            sys.exit()


    def on_connection_request(self):
        """
        Runs code when a request is made to the proxy
        """
        raise NotImplementedError('This feature will be added later')

    def on_ping(self):
        """
        Runs code when a ping request is made to the proxy
        """
        print(f'[>] ({self.downstream_address[0]}:{self.downstream_address[1]}) PINGED {self.conn_hostname} ({self.upstream_address[0]}:{self.upstream_address[1]})')

    def on_invalid_hostname_ping(self):
        """
        Runs code when a ping requests an invalid hostname
        """
        print(
            f'[>] ({self.downstream_address[0]}:{self.downstream_address[1]}) PINGED {self.conn_hostname} [INVALID HOSTNAME]')

    def on_player_connect(self):
        """
        Runs code when a new connection to a server is made
        """
        print(f'[>] {self.player_username} ({self.downstream_address[0]}:{self.downstream_address[1]})  JOINED  {self.conn_hostname} ({self.upstream_address[0]}:{self.upstream_address[1]})')


    def on_player_disconnect(self):
        """
        Runs code upon connection loss
        """
        print(f'[>] {self.player_username} ({self.downstream_address[0]}:{self.downstream_address[1]})  LEFT  {self.conn_hostname} ({self.upstream_address[0]}:{self.upstream_address[1]})')
        print(f'[?] Connection used {self.conn_bandwidth/1000000}MB of bandwidth!')

    def on_server_offline(self):
        """
        Runs code after a connection is closed due to
        the server being unresponsive during connection
        """
        print( f'[>] ({self.downstream_address[0]}:{self.downstream_address[1]})  CONNECTION FAILED  {self.conn_hostname} ({self.upstream_address[0]}:{self.upstream_address[1]}) [SERVER OFFLINE]')

