import os
import json
import logging
from gamma.config import ProxyConfig
from gamma.config import BaseConfigManager

logger = logging.getLogger()

class LocalConfigManager(BaseConfigManager):
    def __init__(self):
        super().__init__()
        self.config_folder = './config/'

    def get(self, hostname:str) -> ProxyConfig|None:
        try:
            if hostname in os.listdir(os.path.join(self.config_folder)):
                with open(os.path.join(self.config_folder, hostname)) as file:
                    config_json = json.load(file)
                    file.close()
                config = self._parse_config(hostname=hostname, data=config_json)
                return config
        except Exception as error:
            logger.exception(f'Error while fetching config for `{hostname}`: {error}')
