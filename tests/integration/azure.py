import datetime
import logging
import json
import sys
import subprocess
from azurewrapper import AzureWrapper
from os import path

from .sshclient import RemoteClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AZURE:
    """Handle resources in Azure cloud"""

    @classmethod
    def fixture(cls, config) -> RemoteClient:
        logger.info(json.dumps(config))
        azure = AZURE(config)
        logger.debug(json.dumps(config))
        instance = azure.create_vm(config)
        ssh = None
        try:
            ssh = RemoteClient(
                host=instance["publicIpAddress"],
                user=config["user"],
                ssh_key_filepath=config["ssh_key_filepath"],
                passphrase=config["passphrase"],
                remote_path=config["remote_path"],
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
            if azure is not None:
                azure.__del__()

    def __init__(self, config):
        """
        Create instance of AZURE class

        :param config: configuration
        """
        self.config = config
        self.az = AzureWrapper(config)


    def __del__(self):
        """Cleanup resources held by this object"""
        if self.instance:
            self.terminate_vm(self.instance)
            self.instance = None


    def import_key(self, config):
        if self.az.get_ssh_key(config["ssh_key_name"]) == None:
            self.az.upload_ssh_key(config["ssh_key_path"], config["ssh_key_name"])

    def create_vm(self, config):
        if self.az.get_nsg(config["nsg_name"]) == None:
            self.az.create_nsg(config["nsg_name"])
        self.instance = self.az.create_vm(config["image_name"], "integration-test" , config["user"], config["nsg_name"], config["ssh_key_name"], "Standard_B1s")
        self.instance_view = self.az.get_vm("integration-test")
        return self.instance


    def terminate_vm(self, instance):
        pass
#        self.az.terminate_vm(self.instance["id"])
 #       self.az.delete_disk(self.instance_view["storageProfile"]["osDisk"]["managedDisk"]["id"])
  #      self.az.delete_vm_nic(self.instance_view["networkProfile"]["networkInterfaces"][0]["id"])
   #     self.az.delete_nsg(self.config["nsg_name"])
