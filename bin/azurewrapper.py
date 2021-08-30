
import subprocess
import logging
import json

class AzureWrapper:
    """Wrapper module to allow both, API as well as az tool usage"""

    def __init__(self, config):
    	pass

    def create_vm(self, subscription, image, name, resource_group, admin_username, nsg, ssh_key_name, size):
        cmd = [ "az", "vm", "create", "--image", image, "--name", name, "--resource-group", resource_group, "--admin-username", admin_username, "--nsg", nsg, "--ssh-key-name", ssh_key_name, "--size", size]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to create vm %s" % result.stderr.decode('utf-8'))
        doc = json.loads(result.stdout)
        return doc["id"]

    def terminate_vm(self, subscription, resource_group, id):
        cmd = [ "az", "vm", "delete", "--resource-group", resource_group, "--subscription", subscription, "--resource-group", resource_group, "--yes", "--ids", id]        
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return Excpetion("Unable to terminate vm %s" % result.stderr.decode("utf-8"))


    def get_nsg(self, subscription, name, resource_group):
        cmd = ["az", "network", "nsg", "show", "--subscription", subscription, "--name", name, "--resource-group", resource_group]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return None
        return json.loads(result.stdout)

    def delete_nsg(self, subscription, name, resource_group):
        cmd = ["az", "network", "nsg", "delete", "--subscription", subscription, "--name", name, "--resource-group", resource_group]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return Excpetion("Unable to delete nsg %s" % result.stderr.decode("utf-8"))


    def create_nsg(self, name, resource_group, subscription):        
        cmd = ["az", "network", "nsg", "create", "--name", name, "--resource-group", resource_group]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Excpetion("Unable to create network security group: %s" + result.stderr.decode('utf-8'))

        cmd = ["az", "network", "nsg", "rule", "create", "--name", "ssh", "--nsg-name", name, "--priority", 300, "--access", "Allow", "--protocol", "Tcp", "--source-address-prefixes", "0.0.0.0/1 128.0.0.0/1", "--subscription", subscription]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exeption("Unableto add rule to nsg %s" % result.stderr.decode("utf-8"))


    def get_ssh_key(self, subscription, resource_group, ssh_keyname):
        cmd = [
            "az", "sshkey", "show", "--subscription", self.subscription, "--resource-group", self.resource_group, "--name", ssh_keyname)
        ]
        if result.returncode != 0:
            return None
        else:
            return json.loads(result.stdout)


    def upload_ssh_key(self, subscription, resource_group, ssh_keypath, ssh_keyname):
        k = paramiko.RSAKey.from_private_key_file(os.path.abspath(ssh_keypath))
        pub = k.get_name() + " " + k.get_base64()
        logger.info("Uploading key %s" % ssh_keyname)
        cmd = [
            os.path.join(self.repo_root, "az"), "sshkey", "create", "--subscription", subscription, "--resource-group", resource_group, "--public-key", pub, "--name", ssh_keyname)
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Error uploading key: %s" % (result.stderr.decode("utf-8")))


    def delete_ssh_key(self, subscription, resource_group, ssh_keyname):
        raise Exception("not yet implemented")
        