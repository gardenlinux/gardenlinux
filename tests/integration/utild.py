import subprocess
import logging
import json

from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)

def get_my_ip():
    """Obtain external visible IP address"""
    cmd = [ "curl", "-4", "https://api.myip.com" ]
    logger.debug("Running %s" % " ".join([v for v in cmd]))
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise Exception("Unable to obtain my public IP: %s" % result.stderr.decode("utf-8"))
    doc = json.loads(result.stdout)
    return doc["ip"]

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
