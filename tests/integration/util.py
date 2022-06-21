import logging
import json
import urllib.request

import paramiko

logger = logging.getLogger(__name__)

def get_my_ip():
    """Obtain external visible IP address"""
    #url='https://api.myip.com'
    url='https://api.ipify.org?format=json'

    response = urllib.request.urlopen(url)
    if response.status != 200:
        raise Exception(f'Unable to obtain this hosts public IP, got HTTP status {response.status} from {url}')
    doc = json.load(response)
    return doc['ip']

def get_public_key(private_key_file):
    k = paramiko.RSAKey.from_private_key_file(private_key_file)
    return k.get_name() + " " + k.get_base64()

def get_config_value(config, key):
    if key in config and config[key] != "":
        return config[key]
    else:
        return None