import json
import logging
import os
import sys
import pytest
import time
import uuid
import tempfile
import requests
import base64

from os import path
from urllib.request import urlopen
from urllib.parse import urlparse

import google.oauth2.service_account
from google.oauth2.service_account import Credentials
import google.cloud.compute as compute
import google.cloud.storage as storage

from helper.sshclient import RemoteClient
from . import util

logger = logging.getLogger(__name__)

startup_script = """#!/bin/bash
touch /tmp/startup-script-ok
"""

class GCP:
    """Handle resources in GCP"""

    @classmethod
    def fixture(cls, credentials, config, imageurl, test_name):
        GCP.validate_config(config, imageurl, test_name, credentials)

        logger.info(f"Setting up testbed for image {imageurl}...")

        gcp = GCP(config, credentials, test_name)
        gcp.init_environment(imageurl)
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


    @classmethod
    def validate_config(cls, cfg: dict, image: str, test_name: str, credentials):
        if not 'project' in cfg:
            cfg['project'] = credentials.project_id
        if not 'image_project' in cfg:
            cfg['image_project'] = cfg['project']
        if not 'image_region' in cfg:
            cfg['image_region'] = "eu-central-1"
        if not 'region' in cfg:
            pytest.exit("GCP region not specified, cannot continue.", 1)
        if not 'zone' in cfg:
            pytest.exit("GCP zone not specified, cannot continue.", 1)
        if not image and not 'image_name' in cfg and not 'image' in cfg:
            pytest.exit("Neither 'image' nor 'image_name' specified, cannot continue.", 3)
        if not 'image_name' in cfg:
            cfg['image_name'] = f"img-{test_name}"
        if not 'bucket' in cfg:
            cfg['bucket'] = f"gl-upload-{test_name}"
        if not 'keep_running' in cfg:
            cfg['keep_running'] = False
        if not 'machine_type' in cfg:
            cfg['machine_type'] = 'n1-standard-2'
        if not 'ssh' in cfg or not cfg['ssh']:
            cfg['ssh'] = {}
        if not 'ssh_key_filepath' in cfg['ssh']:
            import tempfile
            keyfile = tempfile.NamedTemporaryFile(prefix=f"sshkey-{test_name}-", suffix=".key", delete=False)
            keyfp = RemoteClient.generate_key_pair(
                filename = keyfile.name,
            )
            logger.info(f"Generated SSH keypair with fingerprint {keyfp}.")
            cfg['ssh']['ssh_key_filepath'] = keyfile.name
        if not 'ssh_key_name' in cfg['ssh']:
            cfg['ssh']['ssh_key_name'] = f"key-{test_name}"
        if not 'user' in cfg['ssh']:
            cfg['ssh']['user'] = "gardenlinux"
        if not 'uefi' in cfg:
            cfg['uefi'] = False
        if not 'secureboot' in cfg:
            cfg['secureboot'] = False
        if not 'secureboot_parameters' in cfg:
            cfg['secureboot_parameters'] = {}
        if not 'db_path' in cfg['secureboot_parameters']:
            cfg['secureboot_parameters']['db_path'] = "/gardenlinux/cert/secureboot.db.auth"
        if not 'kek_path' in cfg:
            cfg['secureboot_parameters']['kek_path'] = "/gardenlinux/cert/secureboot.kek.auth"
        if not 'pk_path' in cfg:
            cfg['secureboot_parameters']['pk_path'] = "/gardenlinux/cert/secureboot.pk.auth"
        if not 'cert_file_type' in cfg:
            cfg['secureboot_parameters']['cert_file_type'] = 'BIN'


    def _gcp_create_bucket(self, bucket_name):
        bucket = self._storage.bucket(bucket_name=bucket_name)
        if bucket.exists():
            return bucket
        bucket.location = self.config["region"]
        bucket.storage_class = "STANDARD"
        bucket.labels = self._tags
        bucket.create()
        bucket.make_private()


    def _gcp_wait_for_operation(self, operation, timeout=120):
        self.logger.info(f"Waiting for {operation.name} to complete...")
        result = operation.result(timeout=timeout)
        self.logger.info(f"{operation.name} done.")


    def _gcp_create_firewall_rules(self, fw_rest_body):
        rule_name = fw_rest_body["name"]
        self.logger.info(f"Inserting firewall rule {rule_name}...")
        operation = self._compute_firewalls.insert(project=self.project, firewall_resource=fw_rest_body)
        self._gcp_wait_for_operation(operation)
        return rule_name


    def _gcp_create_vpc(self):
        network_name = f"vpc-{self.test_name}"
        subnet_cidr = "10.242.10.0/24"

        self.logger.info(f"Creating VPC {network_name}...")
        vpc_rest_body = {
            "auto_create_subnetworks": False,
            "description": "vpc for Garden Linux integration tests",
            "mtu": 1460,
            "name": network_name,
            "routing_config": {
                "routing_mode": "REGIONAL"
            }
        }
        operation = self._compute_networks.insert(project=self.project, network_resource=vpc_rest_body)
        vpc_selflink = self._compute_networks.get(network=network_name, project=self.project).self_link
        self._gcp_wait_for_operation(operation)

        self.logger.info(f"Creating subnet with CIDR {subnet_cidr} in VPC {network_name} and region {self.region}...")
        subnet_rest_body = {
            "description": "Subnet for Garden Linux integration tests",
            "enable_flow_logs": False,
            "ip_cidr_range": subnet_cidr,
            "name": network_name,
            "network": vpc_selflink,
            "private_ip_google_access": False,
            "region": self.region
        }
        operation = self._compute_subnetworks.insert(project=self.project, region=self.region, subnetwork_resource=subnet_rest_body)
        self._gcp_wait_for_operation(operation)
        return network_name


    def _gcp_delete_vpc(self, name):
        self.logger.info(f"Deleting subnets from VPC {name}...")
        operation = self._compute_subnetworks.delete(project=self.project, region=self.region, subnetwork=name)
        self._gcp_wait_for_operation(operation)
        
        self.logger.info(f"Deleting VPC {name}...")
        operation = self._compute_networks.delete(project=self.project, network=name)
        self._gcp_wait_for_operation(operation)


    def __init__(self, config, credentials, test_name):
        """
        Create instance of GCP class

        :param config: configuration
        """
        self.config = config
        self.ssh_config = config["ssh"]
        self.test_name = test_name
        self.test_uuid = str(uuid.uuid4())

        self._tags = {
            "component": "gardenlinux",
            "test-type": "integration-test",
            "test-name": self.test_name,
            "test-uuid": str(uuid.uuid4()),
        }

        self.logger = logging.getLogger("gcp-testbed")

        self.logger.info(f"This test's tags are:")
        for key in self._tags:
            self.logger.info(f"\t{key}: {self._tags[key]}")

        self.project = config["project"]
        
        os.environ["GOOGLE_CLOUD_PROJECT"] = self.project
        self._compute_networks = compute.NetworksClient(credentials=credentials)
        self._compute_subnetworks = compute.SubnetworksClient(credentials=credentials)
        self._compute_firewalls = compute.FirewallsClient(credentials=credentials)
        self._compute_images = compute.ImagesClient(credentials=credentials)
        self._compute_instances = compute.InstancesClient(credentials=credentials)
        self._storage = storage.Client(credentials=credentials)

        self.network_tags = [f"network-{test_name}"]

        self._bucket = None
        self._image = None
        self._firewall_rules = None
        self._vpc_name = None
        self._instance = None
        self._instance_name = None

        self.zone = config["zone"]
        self.region = config["region"]
        self.image_name = self.config["image_name"]
        self.image_project = self.config["image_project"]
        self.machine_type = self.config["machine_type"]
        self.ssh_key_filepath = path.expanduser(self.ssh_config["ssh_key_filepath"])
        self.user = self.ssh_config["user"]


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


    def init_environment(self, image = None):
        if image:
            self._upload_image(self.image_name, image)
        elif "image" in self.config and self._get_image(self.image_project, self.image_name) == None:
            self._upload_image(self.image_name, self.config["image"])
        self._vpc_name = self._gcp_create_vpc()
        self._firewall_rules = self._ensure_firewall_rules(self._vpc_name)

    def __del__(self):
        """Cleanup resources held by this object"""
        self.clean_test_resources()


    def clean_test_resources(self):
        if "keep_running" in self.config and self.config['keep_running'] == True:
            logger.info(f"Keeping all test resources alive.")
            return

        self.logger.info("Cleaning up test resources...")
        if self._instance:
            self.delete_vm(self._instance)
            self._instance = None
        if self._firewall_rules:
            self._gcp_delete_firewall_rules(self._firewall_rules)
            self._firewall_rules = None
        if self._vpc_name:
            self._gcp_delete_vpc(self._vpc_name)
            self._vpc_name = None
        if self._image:
            self._delete_image(self._image.name)
            self._image = None
        if self._bucket:
            self._delete_bucket(self._bucket.name)
            self._bucket = None


    def _ensure_firewall_rules(self, network):
        myip = util.get_my_ip()

        rules = {
            "name": f"fw-{self.test_name}",
            "allowed": [
                {
                    "I_p_protocol": "tcp",
                    "ports": [
                        "22"
                    ]
                },
                {
                    "I_p_protocol": "icmp"
                }
            ],
            "description": "allow incoming SSH and ICMP for Garden Linux integration tests",
            "direction": "INGRESS",
            "kind": "compute#firewall",
            "log_config": {
                "enable": False
            },
            "network": f"projects/{self.config['project']}/global/networks/{network}",
            "priority": 1000,
            "source_ranges": [myip],
            "target_tags": self.network_tags,
        }

        return self._gcp_create_firewall_rules(rules)


    def _ensure_bucket(self, name):
        bucket = self._storage.bucket(bucket_name=name)
        if bucket.exists():
            self.logger.info(f"Using existing GCS bucket {name} for image upload.")
            return bucket

        self.logger.info(f"Creating GCS bucket {name} for image upload...")
        bucket.storage_class = storage.constants.STANDARD_STORAGE_CLASS

        bucket.iam_configuration.public_access_prevention = (
            storage.constants.PUBLIC_ACCESS_PREVENTION_ENFORCED
        )
        bucket.labels = self._tags
        bucket.create(location=self.config['region'])
        return bucket


    def _delete_bucket(self, name):
        bucket = self._storage.get_bucket(name)
        if bucket.labels == self._tags:
            self.logger.info(f"Deleting GCS bucket {name}...")
            for blob in bucket.list_blobs():
                if blob.metadata == self._tags:
                    blob.delete()
                else:
                    self.logger.info(f"Unable to delete bucket {name} as it contains a blob ({blob.name}) that was not created by this test.")
            bucket.delete()
        else:
            self.logger.info(f"Keeping GCS bucket {name} as it was not created by this test.")

    def _get_file_content_buffer(self, path, file_type):
        if os.path.isfile(path):
            with open(path, 'rb') as f:
                return compute.FileContentBuffer(content=base64.b64encode(f.read()), file_type=file_type)
        else:
            self.logger.error(f"Secureboot key or db {path} does not exists")
            os._exit(os.EX_IOERR)

    def _upload_image(self, image_name, image):
        blob_name = image_name + ".tar.gz"
        self._bucket = self._ensure_bucket(name=self.config["bucket"])

        image_blob = self._bucket.blob(blob_name)
        image_blob.metadata = self._tags

        if not image_blob.exists():
            o = urlparse(image)
            if o.scheme == "file":
                self.logger.info(f"Uploading image {image} - this may take a while...")
                with open(o.path, "rb") as tfh:
                    image_blob.upload_from_file(
                        tfh,
                        content_type='application/x-tar',
                    )

            elif o.scheme == "s3":
                image_region = self.config['image_region']
                s3_url = f"https://{o.hostname}.s3.{image_region}.amazonaws.com/{o.path.lstrip('/')}"
                meta = urlopen(s3_url)
                file_size = int(meta.getheader('Content-Length'))
                chunk_size = 4 * 1024 * 1024

                self.logger.info(f"Downloading from {s3_url} ({file_size} bytes) to temporary file...")
                with tempfile.TemporaryFile() as tfh:
                    with requests.get(s3_url, stream=True) as r:
                        for chunk in r.iter_content(chunk_size=chunk_size): 
                            tfh.write(chunk)

                    tfh.seek(0)

                    self.logger.info(f"Re-uploading image to gs://{self._bucket.name}/{image_blob.name} ({file_size} bytes)...")
                    image_blob.upload_from_file(
                        tfh,
                        size=file_size,
                        content_type='application/x-tar',
                        timeout=600
                    )

            self.logger.info(f"Image blob successfully uploaded to gs://{self._bucket.name}/{image_blob.name}")
        else:
            self.logger.info(f"Image file {image_blob.name} already exists in bucket {self._bucket}.")

        images = self._compute_images

        blob_url = image_blob.public_url
        self.logger.info(f'Importing {blob_url} as {image_name=} into project {self.image_project}')
        config = {
            'description': 'gardenlinux',
            'name': image_name,
            'raw_disk': {
                'source': blob_url,
            },
            'labels': self._tags,
        }

        if self.config['uefi'] or self.config['secureboot']:
            config['guest_os_features'] = [{'type_': "UEFI_COMPATIBLE"}]

        if self.config['secureboot']:
            cert_file_type = self.config['secureboot_parameters']['cert_file_type']
            config['shielded_instance_initial_state'] = {
                'dbs': [self._get_file_content_buffer(self.config['secureboot_parameters']['db_path'], cert_file_type)],
                'keks': [self._get_file_content_buffer(self.config['secureboot_parameters']['kek_path'], cert_file_type)],
                'pk': self._get_file_content_buffer(self.config['secureboot_parameters']['pk_path'], cert_file_type),
            }

        operation = images.insert(project=self.image_project, image_resource=config)
        self._gcp_wait_for_operation(operation)
        image_blob.delete()
        self.logger.info(f'Uploaded image {blob_url} to project {self.project} as {image_name}')
        self._image = images.get(image=image_name, project=self.image_project)

    def _delete_image(self, image_name):
        image = self._compute_images.get(image=image_name, project=self.image_project)
        if image.labels == self._tags:
            self.logger.info(f"Deleting image {image_name}...")
            request = self._compute_images.delete(project=self.image_project, image=image_name)
        else:
            self.logger.info(f"Keeping image {image_name} in project {self.image_project} as it was not created by this test.")

    def _get_image(self, project, image_name):
        """Get image with given name

        :param image_name: name of the image
        """
        self.logger.debug(f"Looking for {image_name=} in {project=}")
        try:
            response = (
                self._compute_images.get(project=project, image=image_name,)
            )
            image = response.self_link
            return image
        except:
            self.logger.debug(f"Failed to find image in {project=}")
            return None

    def _wait_until_reachable(self, hostname):
        self.logger.info(f"Waiting for {hostname} to respond...")
        i = 0
        while i < 20:
            response = os.system("timeout 1 bash -c \"</dev/tcp/" + hostname + "/22\"")
            if response == 0:
                self.logger.info(f"Instance {hostname} is reachable...")
                return
            self.logger.info(f"Waiting for {hostname} to respond...")
            time.sleep(2)
            i += 1
        raise Exception("Remote host unreachable")


    def create_vm(self):
        """
        Create a ComputeEngine instance
        - according to the config passed to the constructor
        - enable ssh access

        :returns: instance to enable cleanup
        """
        
        image = self._get_image(self.image_project, self.image_name)

        self.logger.info(f"Starting new instance from image {self.image_name}...")
        machine_type = f"zones/{self.zone}/machineTypes/{self.machine_type}"
        disk_type = f"zones/{self.zone}/diskTypes/pd-ssd"
        name = f"vm-{self.test_name}"
        config = {
            "name": name,
            "machine_type": machine_type,
            "disks": [
                {
                    "boot": True,
                    "auto_delete": True,
                    "initialize_params": {
                        "disk_size_gb": 7,
                        "source_image": image,
                        "disk_type": disk_type,
                    }
                }
            ],
            "network_interfaces": [
                {
                    "subnetwork": f"projects/{self.project}/regions/{self.region}/subnetworks/{self._vpc_name}",
                    "access_configs": [
                        {"type_": "ONE_TO_ONE_NAT", "name": "External NAT"}
                    ],
                }
            ],
            "labels": self._tags,
            "metadata": {
                "kind": "compute#metadata",
                "items": [
                    {
                        "key": "ssh-keys",
                        "value": self.user + ":" + util.get_public_key(self.ssh_key_filepath) 
                    },
                    {
                        "key": "startup-script",
                        "value" : startup_script
                    }
                ]
            },
            "tags": {
                "items": self.network_tags
            },
        }

        if self.config['secureboot']:
            config["shielded_instance_config"] = {
                "enable_secure_boot": True,
                "enable_integrity_monitoring": True,
                "enable_vtpm": True,
            }

        operation = self._compute_instances.insert(project=self.project, zone=self.zone, instance_resource=config)
        self._gcp_wait_for_operation(operation)
        self._instance_name = name
        list_result = (
            self._compute_instances
            .list(request={'project':self.project, 'zone':self.zone, 'filter': f"name = {self._instance_name}"})
        )
        if len(list_result.items) != 1:
            raise KeyError(f"unexpected number of items: {len(list_result['items'])}")
        self._instance = list_result.items[0]
        interface = self._instance.network_interfaces[0]
        access_config = interface.access_configs[0]
        self.public_ip = access_config.nat_i_p
        self.logger.info(f"Successfully created instance {name} with {self.public_ip=}")
        try:
            self._wait_until_reachable(self.public_ip)
        except Exception as e:
            self.logger.error(e)
            sys.exit(os.EX_NOHOST)
        return self._instance, self.public_ip

    def delete_vm(self, instance):
        """ Delete the given ComputeEngine instance

        :param instance: the instance to delete
        """
        self.logger.info(f"Destroying instance {self._instance_name}...")
        operation = self._compute_instances.delete(project=self.project, zone=self.zone, instance=self._instance_name)
        self._gcp_wait_for_operation(operation)
