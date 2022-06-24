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
        self.debug = True

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

        # Address, Port attributed to each connection
        self.downstream_address = kwargs['downstream_addr']
        self.upstream_address = (None, None)

        # MISC CHECKS
        self.found_player_username = False

        ##########################################################

        # Receives initial data from downstream connection
        data = self.downstream_conn.recv(8192)

        self.conn_type = packet.get_conn_type(data) # Gets the connection type: PING, PLAY or UNKNOWN

        # Finds hostname from within the first packet
        self.conn_hostname = packet.get_conn_hostname(data)

        # Gets backend (ip, port) for hostname
        self.upstream_address = server.get_server_backend(self.conn_hostname)

        # If the IP for hostname == None (Not found), return
        # invalid hostname motd to the downstream connection
        if self.upstream_address[0] is None:
            self.downstream_conn.send(message.unknown_hostname_motd())
            self.conn_alive = False
            sys.exit()

        threading.Thread(target=self.upstream, kwargs={'data': data}).start()  # Starts a `PROXY <---> SERVER` thread
        threading.Thread(target=self.downstream).start()  # Starts a `CLIENT <---> PROXY` thread

        sys.exit()



    def upstream(self, **kwargs):
        try:
            self.upstream_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.upstream_conn.connect((self.upstream_address[0], self.upstream_address[1]))

            time.sleep(0.1)

            self.upstream_conn_packets = 0

            if 'data' in kwargs:
                self.upstream_conn.send(kwargs['data'])

            while self.conn_alive:
                data = self.upstream_conn.recv(8192)

                if data:
                    self.upstream_conn_packets += 1
                    self.conn_bandwidth += len(data)
                    self.downstream_conn.send(data)

                if self.conn_type == 'PING' and self.upstream_conn_packets >= 5:
                    self.conn_alive = False
                    self.on_ping()

            self.upstream_conn.close() # Close the connection if self.conn_alive == False

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

        time.sleep(0.1)

        self.downstream_conn_packets = 0
        self.missed_downstream_packets = 0

        try:

            time.sleep(0.5)

            while self.conn_alive:
                data = self.downstream_conn.recv(8192)

                if data:
                    self.downstream_conn_packets += 1

                    self.conn_bandwidth += len(data) # Adds packet length to bandwidth counter

                    self.upstream_conn.send(data) # Relays the data received to the upstream conn (server)

                    if self.player_username is None and self.conn_type in ['PLAY', 'UNKNOWN']: # Checks all packets until a username is found
                        self.player_username = packet.get_player_username(data)
                        if self.player_username is not None and self.conn_type:
                            self.on_player_connect()

                if self.conn_type == 'PING' and self.downstream_conn_packets >= 5:
                    self.conn_alive = False
                    self.on_ping()

            self.downstream_conn.close() # Close the connection if self.conn_alive == False

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


    def on_player_connect(self):
        """
        Runs code when a new connection to a server is made
        """
        print(f'[>] {self.player_username} ({self.downstream_address[0]}:{self.downstream_address[1]}) JOINED {self.conn_hostname} ({self.upstream_address[0]}:{self.upstream_address[1]})')


    def on_player_disconnect(self):
        """
        Runs code upon connection loss
        """
        print(f'[>] {self.player_username} ({self.downstream_address[0]}:{self.downstream_address[1]}) LEFT {self.conn_hostname} ({self.upstream_address[0]}:{self.upstream_address[1]})')
        print(f'[?] Connection used {self.conn_bandwidth/1000000}MB of bandwidth!')
