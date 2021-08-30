import datetime
import logging
import json
import sys
import subprocess
import azurewrapper
from os import path

from .sshclient import RemoteClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AZURE:
    """Handle resources in Azure cloud"""

    @classmethod
    def fixture(cls, config) -> RemoteClient:
        azure = AZURE(config)
        instance = azure.create_vm()
        ssh = None
        try:
            ssh = RemoteClient(
                host=instance.public_dns_name,
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
        if self.security_group_id:
            self.delete_security_group((self.security_group_id))
            self.security_group_id = None

    def create_vm(self):
        if self.wrapper.get_nsg(self.config["subscription"]), self.config["nsg_name"], self.config["resource_group"]) == None:
            self.wrapper.create_nsg_cmd(self.config["nsg_name"], self.config["resource_group"], self.config["subscription"])
        self.vm = self.wrapper.create_vm(self.config["subscription"], self.config["image"],"integration-test" ,self.config["resource_group"], "azureuser", self.config["nsg_name"], self.config["ssh_key_name"], "Standard_B1s")
        return self.vm["id"]


    def terminate_vm(self, instance):
        self.wrapper.terminate_vm(self.config["subscription"]), self.config["resource_group"], self.vm["id"]) == None:
