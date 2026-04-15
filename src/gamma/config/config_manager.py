import logging
from gamma.config import ProxyConfig

logger = logging.getLogger()

class BaseConfigManager:
    def __init__(self):
        pass
    
    @staticmethod
    def get(hostname:str) -> ProxyConfig|None:
        raise NotImplementedError()
    
    @staticmethod
    def _parse_config(hostname:str, data:dict) -> ProxyConfig|None:
        try:
            pconfig = ProxyConfig(hostname=hostname, host=data['host'], port=data['port'])
            pconfig.proxy_protocol = data.get('proxy_protocol', False)
            pconfig.online_mode    = data.get('online_mode', False)
            return pconfig
        except Exception as error:
            logger.exception(f'An exception occurred while parsing proxy config: {error}')
            return None

    @staticmethod
    def _format_config(config:ProxyConfig) -> ProxyConfig|None:
        try:
            config:ProxyConfig = ProxyConfig(hostname=config['hostname'], host_addr=config['host_addr'], host_port=config['host_port'])
            config.proxy_protocol = config.get('proxy_protocol')
            config.online_mode = config.get('online_mode')
            return config
        except Exception as error:
            logger.exception(f'An exception occurred while parsing proxy config: {error}')