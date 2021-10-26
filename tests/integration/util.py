import subprocess
import logging
import json
import urllib.request

import paramiko
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

def get_my_ip():
    """Obtain external visible IP address"""
    url='https://api.myip.com'

    response = urllib.request.urlopen(url)
    if response.status != 200:
        raise Exception(f'Unable to obtain this hosts public IP, got HTTP status {response.status} from {url}')
    doc = json.load(response)
    return doc['ip']

def get_public_key(private_key_file):
    k = paramiko.RSAKey.from_private_key_file(private_key_file)
    return k.get_name() + " " + k.get_base64()

# gcp related
def delete_firewall_rule(compute, project, name):
    try:
        request = compute.firewalls().delete(project=project, firewall=name)
        response = request.execute()
        logger.info(response)
        op_name = response['name']
        logger.info(f'waiting for delete filewall rule {op_name=}')
        wait_for_global_operation(compute, project, op_name)
    except HttpError as h:
        if h.resp.status != 404:
            raise

def ensure_firewall_rules(compute, project, restfw):
    name = restfw["name"]
    delete_firewall_rule(compute, project, name)

    request = compute.firewalls().insert(project=project, body=restfw)
    response = request.execute()
    logger.info(response)
    op_name = response['name']
    logger.info(f'waiting for create filewall rule {op_name=}')
    wait_for_global_operation(compute, project, op_name)


def wait_for_global_operation(compute, project, operation):
    response = compute.globalOperations().wait(project=project, operation=operation,).execute()
    if response["status"] != "DONE":
        logger.error("Operation failed %s" % json.dumps(response, indent=4))
        error = ""
        if "error" in response:
            error = response["error"]
        raise Exception("Operation %s failed: %s" % (operation, error))

def get_config_value(config, key):
    if key in config and config[key] != "":
        return config[key]
    else:
        return None