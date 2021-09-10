import logging
import json
import os
import time
import re
import pathlib
import subprocess
from azurewrapper import AzureWrapper

from .sshclient import RemoteClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AZURE:
    """Handle resources in Azure cloud"""

    @classmethod
    def fixture(cls, config) -> RemoteClient:

        test_name = "gl-test-" + str(int(time.time()))
        if not("resource_group" in config and config["resource_group"] != None):
            config["resource_group"] = "rg-" + test_name
        logger.info("Using resource group %s" % config["resource_group"])

        if not("storage_account_name" in config and config["storage_account_name"] != None):
            config["storage_account_name"] = "sa" + re.sub("-", "", test_name)
        logger.info("Using storage account name %s" % config["storage_account_name"])

        if not("image_name" in config and config["image_name"] != None):
            config["image_name"] = test_name
        logger.info("Image name %s" % config["image_name"])

        azure = AZURE(config)
        azure.init_environment()
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
        self.image_uploaded = False
        self.resource_group_created = False
        self.storage_account_created = False
        self.az = AzureWrapper(config)

    def __del__(self):
        """Cleanup resources held by this object"""
        if "keep_running" in self.config:
            logger.info("Keeping resource group %s and all resources alive." % self.config["resource_group"])
        else:
            if self.instance:
                self.terminate_vm(self.instance)
                self.instance = None
            if self.image_uploaded:
                self.az.delete_image(self.config["image_name"])
            if self.resource_group_created:
                self.az.delete_resource_group(self.config["resource_group"])

    def init_environment(self):

        if self.az.get_resource_group(self.config["resource_group"]) == None:
            self.az.create_resource_group(self.config["location"], self.config["resource_group"])
            self.resource_group_created = True

        if self.az.get_storage_account(self.config["storage_account_name"]) == None:
            self.az.create_storage_account(self.config["storage_account_name"])
            self.storage_account_created = True

        self.import_key(self.config)

        img = self.az.get_image(self.config["image_name"])
        if img == None:
            self.upload_image()
            self.image_uploaded = True
        instance = self.create_vm(self.config)


    def upload_image(self):
        if "image" in self.config:
            repo_root = pathlib.Path(__file__).parent.parent.parent
            image_file = self.config["image"]
            logger.debug("Uploading image %s" % image_file)
            cmd = [
                os.path.join(repo_root, "bin", "make-azure-ami"),
                "--resource-group",
                self.config["resource_group"],
                "--storage-account-name",
                self.config["storage_account_name"],
                "--image-name",
                self.config["image_name"],
                "--image-path",
                self.config["image"]
            ]
            logger.debug("Running command: " + (" ".join([v for v in cmd])))
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                raise Exception("Error uploading image %s" % (result.stderr.decode("utf-8")))
            logger.info("Image %s uploaded as %s." % (image_file, self.config["image_name"]))
            logger.debug("Result of upload_image %s" % (result.stdout.decode("utf-8")))
            self.image_uploaded = True
        else:
            raise Exception("No image with name %s available and no image file given" % self.config["image_name"])


    def import_key(self, config):
        if self.az.get_ssh_key(config["ssh_key_name"]) == None:
            self.az.upload_ssh_key(config["ssh_key_filepath"], config["ssh_key_name"])

    def create_vm(self, config):
        if self.az.get_nsg(config["nsg_name"]) == None:
            self.az.create_nsg(config["nsg_name"])
        self.instance = self.az.create_vm(
            config["image_name"],
            "integration-test",
            config["user"],
            config["nsg_name"],
            config["ssh_key_name"],
            size="Standard_B1s",
            os_disk_size="7"
        )
        logger.info("VM %s created with ip %s" % (self.instance["id"], self.instance["publicIpAddress"]))
        self.instance_view = self.az.get_vm("integration-test")
        return self.instance

    def terminate_vm(self, instance):
        self.az.terminate_vm(self.instance["id"])
        self.az.delete_disk(
            self.instance_view["storageProfile"]["osDisk"]["managedDisk"]["id"]
        )
        self.az.delete_vm_nic(
            self.instance_view["networkProfile"]["networkInterfaces"][0]["id"]
        )
        self.az.delete_nsg(self.config["nsg_name"])
