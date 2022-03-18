import json
import logging
import os
import sys
import time
from datetime import datetime
from os import path
from urllib.parse import urlparse

import paramiko
import googleapiclient.discovery
import google.oauth2.service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource
from google.cloud import storage

from .sshclient import RemoteClient
from . import util


logger = logging.getLogger(__name__)
googleapiclient_logger = logging.getLogger("googleapiclient")
googleapiclient_logger.setLevel(logging.ERROR)

startup_script = """#!/bin/bash
touch /tmp/startup-script-ok
"""

class GCP:
    """Handle resources in GCP"""

    @classmethod
    def fixture(cls, config):

        test_name = "gl-test-" + str(int(time.time()))
        if not "image_name" in config:
            config["image_name"] = test_name

        gcp = GCP(config)
        gcp.init_environment()
        _, public_ip = gcp.create_vm()
        ssh = None
        try:
            ssh = RemoteClient(
                host=public_ip,
                sshconfig=config["ssh"],
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
        self.ssh_config = config["ssh"]
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.config["project"]
        if "service_account_json_path" in config:
        
            credentials: Credentials = self._auth(config)
            self._compute: Resource = googleapiclient.discovery.build(
                "compute", "v1", credentials=credentials, cache_discovery=False
            )
            self._storage = storage.Client(credentials=credentials, project=self.config["project"])
        else:
            # assume application default credentials
            if not "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
                default_path = os.path.join(os.path.expanduser("~"), ".config", ".gcloud", "application_default_credentials.json")
                if os.path.isfile(default_path):
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = default_path
            self._compute: Resource = googleapiclient.discovery.build("compute", "v1")
            self._storage = storage.Client(project=self.config["project"])

        self.project = config["project"]
        self.zone = config["zone"]
        self.image_name = self.config["image_name"]
        self.image_project = self.config["image_project"]
        self.machine_type = self.config["machine_type"]
        self.ssh_key_filepath = path.expanduser(self.ssh_config["ssh_key_filepath"])
        self.user = self.ssh_config["user"]
        self.image_uploaded = False

    def init_environment(self):
        if "image" in self.config and self._get_image(self.image_project, self.image_name) == None:
            self._upload_image(self.image_project, self.image_name, self.config["image"])

        self._ensure_firewall_rules()

    def __del__(self):
        """Cleanup resources held by this object"""
        if "keep_running" in self.config:
            logger.info("VM and all resources are still running.")
        else:
            if self.instance:
                self.delete_vm(self.instance)
                self.instance = None
            if self.image_uploaded:
                self._delete_image(self.config["project"], self.config["image_name"])
            util.delete_firewall_rule(self._compute, self.config["project"], "test-allow-ssh-icmp")

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

    def _ensure_firewall_rules(self):
        myip = util.get_my_ip()

        rules = {
            "name": "test-allow-ssh-icmp",
            "allowed": [
            {
                "IPProtocol": "tcp",
                "ports": [
                    "22"
                ]
            },
            {
                "IPProtocol": "icmp"
            }
            ],
            "description": "Firewall rule for integration tests",
            "direction": "INGRESS",
            "enableLogging": False,
            "kind": "compute#firewall",
            "logConfig": {
              "enable": False
            },
            "network": "projects/" + self.config["project"] + "/global/networks/default",
            "priority": 1000.0,
            "sourceRanges": [ myip ],
            "targetTags": [
                "gardenlinux-integration-test"
            ]
        }
        util.ensure_firewall_rules(self._compute, self.config["project"], rules)
        
    def _bucket_exists(self, name):
        try: 
            self._storage.get_bucket(name)
            return True
        except:
            return False

    def _upload_image(self, project, image_name, image):

            blob_name = image_name + ".tar.gz"
            gcp_bucket = self._storage.get_bucket(self.config["bucket"])
            image_blob = gcp_bucket.blob(blob_name)
            if image_blob.exists():
                raise Exception("Image %s already uploaded in bucket %s." % (blob_name, self.config["bucket"]))
            logger.info("Uploading %s" % image)
            with open(image, "rb") as tfh:
                image_blob.upload_from_file(
                    tfh,
                    content_type='application/x-tar',
                )

            logger.info("Image blob uploaded to %s %s" % (self.config["bucket"], blob_name))

            images = self._compute.images()

            blob_url = "https://storage.cloud.google.com/" + self.config["bucket"] + "/" + blob_name
            logger.info(f'Importing {blob_url} as {image_name=} into {project=}')
            insertion_rq = images.insert(
                project=project,
                body={
                    'description': 'gardenlinux',
                    'name': image_name,
                    'rawDisk': {
                        'source': blob_url,
                    },
                },
            )

            resp = insertion_rq.execute()
            op_name = resp['name']

            logger.info(f'waiting for {op_name=}')
            util.wait_for_global_operation(self._compute, project, op_name)
            image_blob.delete()
            logger.info(f'uploaded image {blob_url} to {image_name}')
            self.image_uploaded = True

    def _delete_image(self, project, image_name):
        request = self._compute.images().delete(project=project, image=image_name)
        response = request.execute()

    def _get_image(self, project, image_name):
        """Get image with given name

        :param image_name: name of the image
        """
        logger.debug(f"Looking for {image_name=} in {project=}")
        try:
            response = (
                self._compute.images().get(project=project, image=image_name,).execute()
            )
            image = response.get("selfLink")
            logger.info(f"{image=}")
            return image
        except:
            logger.debug(f"failed to find image in {project=}")
            return None

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
                    "initializeParams": {"diskSizeGb": 7, "sourceImage": image,},
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
                    },
                    {
                        "key": "startup-script",
                        "value" : startup_script
                    }
                ]
            },
            "tags": {
                "items": [
                    "gardenlinux-integration-test"
                ]
            },
        }

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
