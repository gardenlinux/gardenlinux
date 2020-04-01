import datetime
import json
import logging
import time
from os import path
from pprint import pformat

import googleapiclient.discovery
import google.oauth2.service_account
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import Resource

from .sshclient import RemoteClient


logger = logging.getLogger(__name__)


class GCP:
    """Handle resources in GCP"""

    @classmethod
    def fixture(cls, config):
        gcp = GCP(config)
        instance = gcp.create_vm()
        logger.info(f"{instance=}")
        # ssh = None
        # try:
        #     ssh = RemoteClient(
        #         host=instance.public_dns_name,
        #         user=config["user"],
        #         ssh_key_filepath=config["ssh_key_filepath"],
        #         passphrase=config["passphrase"],
        #         remote_path=config["remote_path"],
        #     )
        #     yield ssh
        # finally:
        #     if ssh is not None:
        #         ssh.disconnect()
        #     if gcp is not None:
        #         gcp.__del__()

    def __init__(self, config):
        """
        Create instance of GCP class

        :param config: configuration
        """
        self.config = config
        credentials: Credentials = self._auth(config)
        self._compute : Resource = googleapiclient.discovery.build('compute', 'v1', credentials=credentials, cache_discovery=False)
        self.project = config['project']
        self.zone = config['zone']
        self.image_name = self.config["image_name"]
        self.ssh_key_filepath = path.expanduser(self.config["ssh_key_filepath"])
        self.user = self.config["user"]

    def _auth(self, config) -> Credentials:
        service_account_json_path = path.expanduser(config["service_account_json_path"])
        if service_account_json_path:
            with open(service_account_json_path, "r") as f:
                service_account_json = f.read()
        if not service_account_json:
            service_account_json = config["service_account_json"]
        return google.oauth2.service_account.Credentials.from_service_account_info(
            json.loads(service_account_json))

    def __del__(self):
        """Cleanup resources held by this object"""

    def get_image(self, project, image_name):
        response = self._compute.images().get(
            project=project,
            image=image_name,
        ).execute()
        image = response.get('selfLink')
        logger.info(f"{image=}")
        return image

    def wait_for_operation(self, operation):
        print(f"Waiting for operation {operation} to finish...")
        while True:
            result = self._compute.zoneOperations().get(
                project=self.project,
                zone=self.zone,
                operation=operation).execute()
            logger.info(f"status={result['status']}")
            if result['status'] == 'DONE':
                print("### done.")
                if 'error' in result:
                    raise Exception(result['error'])
                return result

            time.sleep(1)

    def create_vm(self):
        """
        Create a ComputeEngine instance
        - according to the config passed to the constructor
        - enable ssh access

        :returns: instance to enable cleanup
        """
        image = self.get_image(self.project, self.image_name)

        machine_type = f"zones/{self.zone}/machineTypes/n1-standard-1"
        time = datetime.datetime.now().isoformat().replace(":", "-").split(".")[0].lower()
        name = f"test-{self.image_name}-{time}"
        with open(f"{self.ssh_key_filepath}.pub", "rb") as f:
            public_key_bytes = f.read()
        config = {
            'name': name,
            'machineType': machine_type,
            'disks': [
                {
                    'boot': True,
                    'autoDelete': True,
                    'initializeParams': {
                        'sourceImage': image,
                    }
                }
            ],
            'networkInterfaces': [{
                'network': 'global/networks/default',
                'accessConfigs': [
                    {'type': 'ONE_TO_ONE_NAT', 'name': 'External NAT'}
                ]
            }],

            'metadata': {
                'items': [{
                    'key': 'block-project-ssh-keys',
                    'value': False
                }, {
                    "key": "ssh-keys",
                    "value": f"{self.user}:{public_key_bytes} {self.user}\n"
                }]
            }
        }
        logger.info(pformat(f"{config=}"))

        operation = self._compute.instances().insert(
            project=self.project,
            zone=self.zone,
            body=config).execute()
        logger.info(pformat(f"{operation=}"))
        self.wait_for_operation(operation['name'])

        instance = operation.get('targetLink')
        logger.info(pformat(f"{instance=}"))
        return instance
