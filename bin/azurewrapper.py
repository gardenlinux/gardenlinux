import subprocess
import logging
import json
import paramiko
import os

logger = logging.getLogger(__name__)


class AzureWrapper:
    """Wrapper module to allow both, API as well as az tool usage"""

    def __init__(self, config):
        self.subscription = config["subscription"]
        self.resource_group = config["resource_group"]
        self.location = config["location"]


    def get_image(self, name):
        cmd = [
            "az",
            "image",
            "show",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--name",
            name
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            return None
        doc = json.loads(result.stdout)
        logger.info(json.dumps(doc, indent=4))
        return doc


    def create_vm(self, image, name, admin_username, nsg, ssh_key_name, size, os_disk_size=None):
        cmd = [
            "az",
            "vm",
            "create",
            "--public-ip-sku",
            "Standard",
            "--image",
            image,  
            "--name",
            name,
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--admin-username",
            admin_username,
            "--nsg",
            nsg,
            "--ssh-key-name",
            ssh_key_name,
            "--size",
            size,
        ]
        if os_disk_size != None:
            cmd = cmd + ["--os-disk-size-gb", os_disk_size]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Unable to create vm %s" % result.stderr.decode("utf-8"))
        doc = json.loads(result.stdout)
        logger.info(json.dumps(doc, indent=4))
        return doc

    def get_vm(self, name):
        cmd = [
            "az",
            "vm",
            "get-instance-view",
            "--resource-group",
            self.resource_group,
            "--subscription",
            self.subscription,
            "--name",
            name,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return None
        return json.loads(result.stdout)

    def terminate_vm(self, id):
        cmd = [
            "az",
            "vm",
            "delete",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--yes",
            "--ids",
            id,
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return Exception(
                "Unable to terminate vm %s" % result.stderr.decode("utf-8")
            )

    def delete_image(self, name):
        logging.debug(f"Deleting image {name}")
        cmd = ["az", "image", "delete", 
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--name",
            name
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            logger.error("Unable to delete disk " + result.stderr.decode("utf-8"))
        logger.info(f"Image {name} deleted")


    def delete_disk(self, id):
        cmd = ["az", "disk", "delete", "--yes", "--ids", id]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            logger.error("Unable to delete disk " + result.stderr.decode("utf-8"))

    def delete_vm_nic(self, id):
        cmd = ["az", "network", "nic", "delete", "--ids", id]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            logger.error(
                "Unable to delete network nic " + result.stderr.decode("utf-8")
            )

    def get_nsg(self, name):
        cmd = [
            "az",
            "network",
            "nsg",
            "show",
            "--subscription",
            self.subscription,
            "--name",
            name,
            "--resource-group",
            self.resource_group,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return None
        return json.loads(result.stdout)

    def delete_nsg(self, name):
        cmd = [
            "az",
            "network",
            "nsg",
            "delete",
            "--subscription",
            self.subscription,
            "--name",
            name,
            "--resource-group",
            self.resource_group,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # assume nsg does not exist
            return Exception("Unable to delete nsg %s" % result.stderr.decode("utf-8"))

    def create_nsg(self, name):
        cmd = [
            "az",
            "network",
            "nsg",
            "create",
            "--name",
            name,
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception(
                "Unable to create network security group: %s"
                + result.stderr.decode("utf-8")
            )

        cmd = [
            "az",
            "network",
            "nsg",
            "rule",
            "create",
            "--name",
            "ssh",
            "--nsg-name",
            name,
            "--priority",
            "300",
            "--destination-port-ranges",
            "22",
            "--access",
            "Allow",
            "--protocol",
            "Tcp",
            "--source-address-prefixes",
            "0.0.0.0/1",
            "128.0.0.0/1",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception(
                "Unable to add rule to nsg %s" % result.stderr.decode("utf-8")
            )

    def get_ssh_key(self, ssh_keyname):
        cmd = [
            "az",
            "sshkey",
            "show",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--name",
            ssh_keyname,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            return None
        else:
            return json.loads(result.stdout)

    def upload_ssh_key(self, ssh_keypath, ssh_keyname):
        k = paramiko.RSAKey.from_private_key_file(os.path.abspath(ssh_keypath))
        pub = k.get_name() + " " + k.get_base64()
        logger.info("Uploading key %s" % ssh_keyname)
        cmd = [
            "az",
            "sshkey",
            "create",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--public-key",
            pub,
            "--name",
            ssh_keyname,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            raise Exception("Error uploading key: %s" % (result.stderr.decode("utf-8")))

    def delete_ssh_key(self, ssh_keyname):
        cmd = [
            os.path.join(self.repo_root, "az"),
            "sshkey",
            "delete",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--name",
            ssh_keyname,
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            logger.error("Error deleting ssh key: %s" % result.stderr.decode("utf-8"))

    def get_resource_group(self, name):
        cmd = [
            "az",
            "group",
            "show",
            "--subscription",
            self.subscription,
            "--name",
            name
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # no resource group
            return None
        else:
            return json.loads(result.stdout)

    def create_resource_group(self, location, name):
        cmd = [
            "az",
            "group",
            "create",
            "--subscription",
            self.subscription,
            "--location",
            location,
            "--name",
            name
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # no resource group
            raise Exception("Unable to create resource group %s" % result.stderr.decode('utf-8'))
        else:
            return json.loads(result.stdout)

    def delete_resource_group(self, name):
        cmd = [
            "az",
            "group",
            "delete",
            "--subscription",
            self.subscription,
            "--yes",
            "--name",
            name
        ]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # no resource group
            raise Exception("Unable to delete resource group %s" % result.stderr.decode('utf-8'))
        else:
            return

    def get_storage_account(self, name):
        cmd = [
            "az",
            "storage",
            "account",
            "list",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # no resource group
            raise Exception("Unable to to list storage accounts %s" % result.stderr.decode('utf-8'))

        stg_accounts = json.loads(result.stdout)
        for stg in stg_accounts:
            if stg["name"] == name:
                return stg
        return None

    def create_storage_account(self, name):
        cmd = [
            "az",
            "storage",
            "account",
            "create",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--allow-blob-public-access",
            "false",
            "--min-tls-version",
            "TLS1_2",
            "--https-only",
            "true",
            "--name",
            name
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # no resource group
            raise Exception("Unable to to create storage account %s" % result.stderr.decode('utf-8'))
        stg_account = json.loads(result.stdout)
        logger.debug(json.dumps(stg_account, indent=4))
        return stg_account

    def delete_storage_account(self, name):
        cmd = [
            "az",
            "storage",
            "account",
            "delete",
            "--subscription",
            self.subscription,
            "--resource-group",
            self.resource_group,
            "--name",
            name,
            "--yes"
        ]
        logging.debug("Running %s" % " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # no resource group
            raise Exception("Unable to to delete storage account %s: %s" % (name, result.stderr.decode('utf-8')))
