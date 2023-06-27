import os
import json
import time
import requests

def hostname_config(hostname):
    """
     Fetch netconfig from local storage or API.
    """
    # Fetching via storage/cache
    if hostname in os.listdir('./gamma/assets/cache/netconfig/'):
        try:
            with open(f"./gamma/assets/cache/netconfig/{hostname}", 'r+') as netconfig_file:
                netconfig = json.loads(netconfig_file.read())
                netconfig_file.close()
                if netconfig['cache_expiry'] > time.time():
                    return netconfig
        except:
            pass


    # Fetching via API
    request = requests.get(f'http://0.0.0.0/v1/proxy/config/{hostname}/')
    if request.status_code == 200:
        netconfig = request.json()
        netconfig['cache_expiry'] = time.time() + 10
        with open(f'./gamma/assets/cache/netconfig/{hostname}', 'w+') as netconfig_file:
            netconfig_file.write(json.dumps(netconfig, indent=4))
            netconfig_file.close()
            return netconfig

