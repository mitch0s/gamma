
class ProxyConfig:
    def __init__(self, hostname:str, host:str, port:int, proxy_protocol:bool=False, online_mode:bool=False):
        self.hostname = hostname
        self.host = host
        self.port = port
        self.proxy_protocol = proxy_protocol
        self.online_mode = online_mode