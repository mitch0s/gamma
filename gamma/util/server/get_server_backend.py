import os
import json

def get_server_backend(hostname):
    """
    MUST RETURN TUPLE (ip: str, port: int) at end of function.
    """

    # TODO: Add code to check for hostname backend

    configs = os.listdir('./config')

    for config in configs:
        config_file = open(f'./config/{config}')
        config = json.loads(config_file.read())
        config_file.close()

        if 'hostname' in config:
            if config['hostname'] == hostname:
                host = config['host']
                port = config['port']
                if 'proxy_protocol' in config:
                    proxy_protocol = config['proxy_protocol']
                else:
                    proxy_protocol = False

                return host, port, proxy_protocol

        return None, None, None



#    host = '54.39.130.114'
#   port = 25565
#
#    return host, port
