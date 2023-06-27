import json
import gamma

def config(dir='./config.json') -> None:
    with open(dir) as config_file:
        config = json.loads(config_file.read())

    if 'SERVER_OFFLINE' in config:
        if 'motd' in config['SERVER_OFFLINE']:
            gamma.variable.offline_motd_text = config['SERVER_OFFLINE']['motd']['text']
            gamma.variable.offline_motd_protocol = config['SERVER_OFFLINE']['motd']['protocol']
            gamma.variable.offline_motd_version = config['SERVER_OFFLINE']['motd']['version']
            gamma.variable.offline_motd_icon = config['SERVER_OFFLINE']['motd']['icon']
        if 'disconnect' in config['SERVER_OFFLINE']:
            gamma.variable.offline_disconnect_text = config['SERVER_OFFLINE']['disconnect']['text']

    if 'INVALID_HOSTNAME' in config:
        if 'motd' in config['INVALID_HOSTNAME']:
            gamma.variable.invalid_hostname_motd_text = config['INVALID_HOSTNAME']['motd']['text']
            gamma.variable.invalid_hostname_motd_protocol = config['INVALID_HOSTNAME']['motd']['protocol']
            gamma.variable.invalid_hostname_motd_version = config['INVALID_HOSTNAME']['motd']['version']
            gamma.variable.invalid_hostname_motd_icon = config['INVALID_HOSTNAME']['motd']['icon']
        if 'disconnect' in config['INVALID_HOSTNAME']:
            gamma.variable.invalid_hostname_disconnect_text = config['INVALID_HOSTNAME']['disconnect']['text']
