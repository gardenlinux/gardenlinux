import json
import logging
import os
import time
from datetime import datetime
from os import path
from urllib.parse import urlparse

import paramiko
import googleapiclient.discovery
import google.oauth2.service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource

from .sshclient import RemoteClient


logger = logging.getLogger(__name__)
googleapiclient_logger = logging.getLogger("googleapiclient")
googleapiclient_logger.setLevel(logging.ERROR)


class GCP:
    """Handle resources in GCP"""

    @classmethod
    def fixture(cls, config):
        gcp = GCP(config)
        _, public_ip = gcp.create_vm()
        ssh = None
        try:
            ssh = RemoteClient(
                host=public_ip,
                user=config["user"],
                ssh_key_filepath=config["ssh_key_filepath"],
                passphrase=config["passphrase"],
                remote_path=config["remote_path"],
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()

    def __init__(self, config):
        """
        Create instance of GCP class

        :param config: configuration
        """
        self.config = config
        credentials: Credentials = self._auth(config)
        self._compute: Resource = googleapiclient.discovery.build(
            "compute", "v1", credentials=credentials, cache_discovery=False
        )
        self.project = config["project"]
        self.zone = config["zone"]
        self.image_name = self.config["image_name"]
        self.image_project = self.config["image_project"]
        self.machine_type = self.config["machine_type"]
        self.ssh_key_filepath = path.expanduser(self.config["ssh_key_filepath"])
        self.user = self.config["user"]

    def __del__(self):
        """Cleanup resources held by this object"""
        if self.instance:
            self.delete_vm(self.instance)
            self.instance = None

    def _auth(self, config) -> Credentials:
        """Loads the authentication credentials given in the config

        :param config: the config specifying path to service account json file
                       or the service account credentials json
        """
        service_account_json_path = path.expanduser(config["service_account_json_path"])
        if service_account_json_path:
            with open(service_account_json_path, "r") as f:
                service_account_json = f.read()
        if not service_account_json:
            service_account_json = config["service_account_json"]
        return google.oauth2.service_account.Credentials.from_service_account_info(
            json.loads(service_account_json)
        )

    def _get_image(self, project, image_name):
        """Get image with given name

        :param image_name: name of the image
        """
        response = (
            self._compute.images().get(project=project, image=image_name,).execute()
        )
        image = response.get("selfLink")
        logger.info(f"{image=}")
        return image

    def _wait_for_operation(self, operation):
        """Wait for a GCP operation to finish"""
        logger.info(f"Waiting for {operation} to finish ...")
        while True:
            result = (
                self._compute.zoneOperations()
                .get(project=self.project, zone=self.zone, operation=operation)
                .execute()
            )
            if result["status"] == "DONE":
                logger.info("... done")
                if "error" in result:
                    raise Exception(result["error"])
                return result
            time.sleep(1)

    def _wait_until_reachable(self, hostname):
        logger.info(f"Waiting for {hostname} to respond to ping ...")
        while True:
            response = os.system("ping -c 1 " + hostname)
            if response == 0:
                logger.info(f"... {hostname} is reachable, wait 20 sec more")
                time.sleep(20)
                return
            time.sleep(1)

    def _get_resource_name(self, url):
        """Get resource name from GCP url"""
        return urlparse(url).path.split("/")[-1]

    def get_public_key(self):
        k = paramiko.RSAKey.from_private_key_file(self.ssh_key_filepath)
        return k.get_name() + " " + k.get_base64()

    def create_vm(self):
        """
        Create a ComputeEngine instance
        - according to the config passed to the constructor
        - enable ssh access

        :returns: instance to enable cleanup
        """
        image = self._get_image(self.image_project, self.image_name)

        machine_type = f"zones/{self.zone}/machineTypes/{self.machine_type}"
        time = datetime.now().strftime("%Y-%m-%dt%H-%M-%S")
        # name = f"gardenlinux-test-{self.image_name}-{time}"
        # name too long
        name = f"test-{self.image_name}"
        config = {
            "name": name,
            "machineType": machine_type,
            "disks": [
                {
                    "boot": True,
                    "autoDelete": True,
                    "initializeParams": {"diskSizeGb": 3, "sourceImage": image,},
                }
            ],
            "networkInterfaces": [
                {
                    "network": "global/networks/default",
                    "accessConfigs": [
                        {"type": "ONE_TO_ONE_NAT", "name": "External NAT"}
                    ],
                }
            ],
            "metadata": {
                "kind": "compute#metadata",
                "items": [
                    {
                        "key": "ssh-keys",
                        "value": self.user + ":" + self.get_public_key() 
                    }
                ]
            },
        }
        print(config)
        logger.error(config)

        operation = (
            self._compute.instances()
            .insert(project=self.project, zone=self.zone, body=config)
            .execute()
        )
        self._wait_for_operation(operation["name"])
        url = operation.get("targetLink")
        self.name = self._get_resource_name(url)
        list_result = (
            self._compute.instances()
            .list(project=self.project, zone=self.zone, filter=f"name = {self.name}")
            .execute()
        )
        if len(list_result["items"]) != 1:
            raise KeyError(f"unexpected number of items: {len(list_result['items'])}")
        self.instance = list_result["items"][0]
        interface = self.instance["networkInterfaces"][0]
        access_config = interface["accessConfigs"][0]
        self.public_ip = access_config["natIP"]
        logger.info(f"created instance {url=} with {self.public_ip=}")
        self._wait_until_reachable(self.public_ip)
        return self.instance, self.public_ip

    def delete_vm(self, instance):
        """ Delete the given ComputeEngine instance

        :param instance: the instance to delete
        """
        operation = (
            self._compute.instances()
            .delete(project=self.project, zone=self.zone, instance=self.name)
            .execute()
        )
        self._wait_for_operation(operation["name"])
