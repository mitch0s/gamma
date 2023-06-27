import threading
import time

import gamma
import json

g = gamma.Gamma()
g.debug = True

gamma.load.config(dir='./config.json')
g.bind(host='0.0.0.0', port=25564)  # Bind the socket server.

@gamma.event.hook.downstream_connect
def downstream_connect(Connection):
    match Connection.conn_type:
        case 'PING' : print(f'[PING] {Connection.downstream_addr[0]} --> {Connection.downstream_connect_hostname}')
        case 'PLAY' : print(f'[JOIN] {Connection.downstream_addr[0]} ({Connection.player_username}) --> {Connection.downstream_connect_hostname}')

@gamma.event.hook.downstream_disconnect
def downstream_disconnect(Connection):
    match Connection.conn_type:
        case 'PLAY':
            print(f'[LEAVE] {Connection.downstream_addr[0]} ({Connection.player_username}) --> {Connection.downstream_connect_hostname} [{Connection.upstream_packet_count + Connection.downstream_packet_count} packets] [{round((Connection.downstream_bandwidth + Connection.upstream_bandwidth) / 1_000_000, 1)}Mbit]')

@gamma.event.hook.upstream_connect
def upstream_connect(Connection):
    pass

@gamma.event.hook.upstream_disconnect
def upstream_disconnect(Connection):
    pass

@gamma.event.hook.downstream_packet
def downstream_packet(data, Connection):
    return data

@gamma.event.hook.upstream_packet
def upstream_packet(data, Connection):
    return data




def config_watcher():
    config = {}
    while True:
        with open('config.json', 'r+') as config_file:
            temp_config = json.loads(config_file.read())
            if config != temp_config:
                gamma.load.config(dir='./config.json')
                config = temp_config
                print('Config reloaded!')
        time.sleep(1)

threading.Thread(target=config_watcher).start()
g.listen()  # Begin handling player connections.