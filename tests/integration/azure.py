import logging
import os
import time
import re
import pytest
import uuid

from .sshclient import RemoteClient

from azure.core.exceptions import (
    ResourceExistsError,
    ResourceNotFoundError
)

from urllib.request import urlopen
from urllib.parse import urlparse

from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient

from azure.mgmt.storage.models import StorageAccountCheckNameAvailabilityParameters
from azure.storage.blob import BlobClient

from paramiko import RSAKey


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

azlogger = logging.getLogger('azure')
azlogger.setLevel(logging.ERROR)

testbedlogger = logging.getLogger('azure-testbed')
testbedlogger.setLevel(logging.INFO)

def progress_function(capsys, total, uploaded):
    with capsys.disabled():
        print(f"Uploaded {uploaded} of {total} bytes ({uploaded/total*100:.2f}%)", end='\r', flush=True)


class AZURE:
    """Handle resources in Azure cloud"""

    @classmethod
    def find_subscription_id(cls, credential, subscription_name: str) -> str:
        subscription_client = SubscriptionClient(credential)
        for sub in subscription_client.subscriptions.list():
            if sub.display_name == subscription_name:
                return sub.subscription_id
        raise RuntimeError(f"Cannot find a subscription with display name {subscription_name}")


    def az_get_resource_group(self, name: str):
        try:
            return self.rclient.resource_groups.get(resource_group_name=name)
        except ResourceNotFoundError:
            return None

    def az_create_resource_group(self, name: str, location: str):
        self.logger.info(f"Creating resource group {name}...")
        return self.rclient.resource_groups.create_or_update(
            resource_group_name = name,
            parameters = {
                'location': location,
                'tags': self._tags
            }
        )

    def az_delete_resourcegroup(self, name: str, force: bool = False, wait_for_completion: bool = True):
        rg = self.az_get_resource_group(name)
        if rg.tags == self._tags or force:
            self.logger.info(f"Deleting resource group {name}...")
            poller = self.rclient.resource_groups.begin_delete(
                resource_group_name = name
            )
            if wait_for_completion:
                poller.result()
        else:
            self.logger.info(f"Keeping resource group {name} as it was not created by this test.")


    def az_get_storage_account(self, name: str):
        try:
            return self.sclient.storage_accounts.get_properties(
                resource_group_name=self._resourcegroup.name,
                account_name=name
            )
        except ResourceNotFoundError:
            return None

    def az_create_storage_account(self, name: str):
        availability = self.sclient.storage_accounts.check_name_availability(
            StorageAccountCheckNameAvailabilityParameters(name=name)
        )
        if not availability.name_available:
            raise RuntimeError(f"Storage account name {name} not available: {availability.reason}")
        self.logger.info(f"Creating storage account {name} in resourcegroup {self._resourcegroup.name}...")
        return self.sclient.storage_accounts.begin_create(
            resource_group_name = self._resourcegroup.name,
            account_name = name,
            parameters = {
                'sku': {
                    'name': 'Standard_RAGRS',
                    'tier': 'Standard',
                },
                'kind': 'StorageV2',
                'location': self._resourcegroup.location,
                'allow_blob_public_access': False,
                'enable_https_traffic_only': True,
                'minimum_tls_version': 'TLS1_2',
                'tags': self._tags
            }
        ).result()

    def az_delete_storage_account(self, name: str, force: bool = False):
        saccnt = self.az_get_storage_account(name)
        if saccnt.tags == self._tags or force:
            self.logger.info(f"Deleting storage account {name}...")
            self.sclient.storage_accounts.delete(
                resource_group_name = self._resourcegroup.name,
                account_name = name
            )
        else:
            self.logger.info(f"Keeping storage account {name} as it was not created by this test.")


    def az_get_ssh_key(self, name: str):
        try:
            return self.cclient.ssh_public_keys.get(resource_group_name = self._resourcegroup.name, ssh_public_key_name = name)
        except ResourceNotFoundError:
            return None

    def az_upload_ssh_key(self, name: str, filepath: str):
        keydata = RSAKey.from_private_key_file(os.path.abspath(filepath))
        pubkey = keydata.get_name() + " " + keydata.get_base64()
        self.logger.info(f"Creating SSH key {name} in resourcegroup {self._resourcegroup.name}...")
        return self.cclient.ssh_public_keys.create(
            resource_group_name = self._resourcegroup.name,
            ssh_public_key_name = name,
            parameters = {
                'location': self._resourcegroup.location,
                'public_key': pubkey,
                'tags': self._tags
            }
        )


    def az_get_image(self, name: str):
        try:
            return self.cclient.images.get(resource_group_name = self._resourcegroup.name, image_name = name)
        except ResourceNotFoundError:
            return None

    def az_delete_image(self, name: str, force: bool = False, wait_for_completion: bool = True):
        img = self.az_get_image(name)
        if img.tags == self._tags or force:
            self.logger.info(f"Deleting image {name}...")
            poller = self.cclient.images.begin_delete(
                resource_group_name = self._resourcegroup.name,
                image_name = name
            )
            if wait_for_completion:
                poller.result()
        else:
            self.logger.info(f"Keeping image {name} as it was not created by this test.")


    def az_get_nsg(self, name):
        try:
            return self.nclient.network_security_groups.get(resource_group_name = self._resourcegroup.name, network_security_group_name = name)
        except ResourceNotFoundError:
            return None

    def az_create_nsg(self, name):
        self.logger.info(f"Creating network security group {name} in resourcegroup {self._resourcegroup.name}...")
        nsg = self.nclient.network_security_groups.begin_create_or_update(
            resource_group_name = self._resourcegroup.name,
            network_security_group_name = name,
            parameters = {
                'location': self._resourcegroup.location,
                'tags': self._tags
            }
        ).result()
        self.logger.info(f"Enabling incoming SSH connections to network security group {name}...")
        self.nclient.security_rules.begin_create_or_update(
            resource_group_name = self._resourcegroup.name,
            network_security_group_name = nsg.name,
            security_rule_name = "AllowSshInBound",
            security_rule_parameters = {
                'description': 'allow incoming SSH',
                'protocol': 'Tcp',
                'source_port_range': '*',
                'destination_port_range': '22',
                'access': 'Allow',
                'priority': 300,
                'direction': 'Inbound',
                'source_address_prefixes': {'0.0.0.0/1', '128.0.0.0/1'},
                'destination_address_prefix': 'VirtualNetwork',
            }
        ).result()
        return nsg

    def az_delete_nsg(self, name, force: bool = False, wait_for_completion: bool = True):
        nsg = self.az_get_nsg(name)
        if nsg.tags == self._tags or force:
            self.logger.info(f"Deleting network security group {name}...")
            poller = self.nclient.network_security_groups.begin_delete(
                resource_group_name = self._resourcegroup.name,
                network_security_group_name = name
            )
            if wait_for_completion:
                poller.result()
        else:
            self.logger.info(f"Keeping network security group {name} as it was not created by this test.")


    def az_create_vm(self, name: str, admin_username: str = 'azureuser', vm_size: str = 'Standard_B2s', disk_size: int = 7):
        self.logger.info("Creating virtual network...")
        self._network = self.nclient.virtual_networks.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            virtual_network_name=f"{name}-Vnet",
            parameters={
                'location': self._resourcegroup.location,
                'address_space': {
                    'address_prefixes': ['10.0.0.0/24'],
                },
                'tags': self._tags
            }
        ).result()

        self.logger.info(f"Creating subnet in virtual network {self._network.name} with network security group {self._nsg.name}...")
        self._subnet = self.nclient.subnets.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            virtual_network_name=self._network.name,
            subnet_name=f"{name}-Subnet",
            subnet_parameters={
                'address_prefix': '10.0.0.0/24',
                'network_security_group': self._nsg,
                'tags': self._tags
            }
        ).result()

        self.logger.info(f"Creating public IP address in subnet {self._subnet.name}...")
        self._ipaddress = self.nclient.public_ip_addresses.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            public_ip_address_name=f"{name}-PublicIp",
            parameters={
                'location': self._resourcegroup.location,
                'sku': {
                    'name': 'Standard'
                },
                'public_ip_allocation_method': 'Static',
                'public_ip_address_version' : 'IPV4',
                'tags': self._tags
            }
        ).result()

        self.logger.info(f"Creating network interface for IP address {self._ipaddress.name} ({self._ipaddress.ip_address})...")
        self._nic = self.nclient.network_interfaces.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            network_interface_name=f"{name}-VmNic",
            parameters={
                'location': self._resourcegroup.location,
                'ip_configurations': [
                    {
                        'name': f"{name}-IpAddressConfig",
                        'subnet': {
                            'id': self._subnet.id
                        },
                        'public_ip_address': {
                            'id': self._ipaddress.id
                        }
                    }
                ],
                'tags': self._tags
            }
        ).result()

        self.logger.info(f"Creating and booting Virtual machine from image {self._image.name}...")
        self._instance = self.cclient.virtual_machines.begin_create_or_update(
            resource_group_name=self._resourcegroup.name,
            vm_name=name,
            parameters={
                'location': self._resourcegroup.location,
                'storage_profile': {
                    'image_reference': {
                        'id': self._image.id
                    },
                    'os_disk': {
                        'disk_size_gb': disk_size,
                        'create_option': 'FromImage',
                        'delete_option': 'Delete'
                    }
                },
                'hardware_profile': {
                    'vm_size': vm_size,
                },
                'os_profile': {
                    'computer_name': name,
                    'admin_username': admin_username,
                    'linux_configuration': {
                        'disable_password_authentication': True,
                        'ssh': {
                            'public_keys': [
                                {
                                    'path': f"/home/{admin_username}/.ssh/authorized_keys",
                                    'key_data': self._ssh_key.public_key,
                                }
                            ]
                        }
                    }
                },
                'network_profile': {
                    'network_interfaces': [
                        {
                            'id': self._nic.id,
                        }
                    ]
                },
                'tags': self._tags
            }
        ).result()

        self.logger.info(f"Virtual machine {name} with IP {self._ipaddress.ip_address} successfully created!")
        return self._instance

    def az_terminate_vm(self, name: str):
        self.logger.info(f"Terminating virtual machine {self._instance.name}...")

        self.cclient.virtual_machines.begin_delete(
            resource_group_name = self._resourcegroup.name,
            vm_name = name
        ).result()
        
        self.nclient.network_interfaces.begin_delete(
            resource_group_name=self._resourcegroup.name,
            network_interface_name=self._nic.name
        ).result()

        self.nclient.public_ip_addresses.begin_delete(
            resource_group_name=self._resourcegroup.name,
            public_ip_address_name=self._ipaddress.name
        ).result()

        self.nclient.subnets.begin_delete(
            resource_group_name=self._resourcegroup.name,
            virtual_network_name=self._network.name,
            subnet_name=self._subnet.name
        ).result()

        self.nclient.virtual_networks.begin_delete(
            resource_group_name=self._resourcegroup.name,
            virtual_network_name=self._network.name
        ).result()


    @classmethod
    def validate_config(cls, cfg: dict, image: str, test_name: str):
        if not 'location' in cfg:
            pytest.exit("Azure location not specified, cannot continue.", 1)
        # if not 'subscription' in cfg and not 'subscription_id' in cfg:
        #     pytest.exit("Azure subscription name or subscription ID not specified, cannot continue.", 2)
        if not image and not 'image_name' in cfg and not 'image' in cfg:
            pytest.exit("Neither 'image' nor 'image_name' specified, cannot continue.", 3)
        if not 'image_name' in cfg:
            cfg['image_name'] = f"img-{test_name}"
        if not 'resource_group' in cfg:
            cfg['resource_group'] = f"rg-{test_name}"
        if not 'storage_account_name' in cfg:
            cfg['storage_account_name'] = f"sa{re.sub('-', '', test_name)}"
        if not 'nsg_name' in cfg:
            cfg['nsg_name'] = f"nsg-{test_name}"
        if not 'keep_running' in cfg:
            cfg['keep_running'] = False
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
            cfg['ssh']['user'] = "azureuser"


    @classmethod
    def fixture(cls, credentials, config, imageurl) -> RemoteClient:
        test_name = f"gl-test-{time.strftime('%Y%m%d%H%M%S')}"
        AZURE.validate_config(config, imageurl, test_name)

        logger.info(f"Setting up testbed for image {imageurl}...")
        logger.info("Using resource group %s" % config["resource_group"])
        logger.info("Using storage account name %s" % config["storage_account_name"])
        logger.info("Using image name %s" % config["image_name"])

        azure = AZURE(credentials, config, imageurl, test_name)
        azure.init_environment()
        (instance, ip) = azure.create_vm(config)
        ssh = None
        try:
            ssh = RemoteClient(
                host=ip.ip_address,
                sshconfig=config["ssh"],
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
            if azure is not None:
                azure.cleanup_test_resources()


    def __init__(self, credentials, config, imageurl, test_name):
        """
        Create instance of AZURE class

        :param config: configuration
        """
        self.config = config
        if imageurl:
            self.config['image'] = imageurl
        self.ssh_config = config["ssh"]
        self.test_name = test_name

        self._tags = {
            "component": "gardenlinux",
            "test-type": "integration-test",
            "test-name": self.test_name,
            "test-uuid": str(uuid.uuid4()),
        }

        self.logger = logging.getLogger("azure-testbed")
        self.logger.info(f"Using {credentials.subscription_id=} for tests")

        self.cclient = ComputeManagementClient(credentials.credential, credentials.subscription_id)
        self.rclient = ResourceManagementClient(credentials.credential, credentials.subscription_id)
        self.sclient = StorageManagementClient(credentials.credential, credentials.subscription_id)
        self.nclient = NetworkManagementClient(credentials.credential, credentials.subscription_id)


    def __del__(self):
        """Cleanup resources held by this object"""
        self.cleanup_test_resources()

    def cleanup_test_resources(self):
        if "keep_running" in self.config and self.config['keep_running'] == True:
            logger.info(f"Keeping resource group {self._resourcegroup.name} and all resources in it alive.")
            return

        if self._instance:
            self.az_terminate_vm(self._instance.name)
            self._instance = None
        if self._nsg:
            self.az_delete_nsg(name=self._nsg.name)
            self._nsg = None
        if self._image:
            self.az_delete_image(name=self._image.name)
            self._image = None
        if self._storageaccount:
            self.az_delete_storage_account(self._storageaccount.name)
            self._storageaccount = None
        if self._resourcegroup:
            self.az_delete_resourcegroup(name=self._resourcegroup.name, wait_for_completion=False)
            self._resourcegroup = None

    def init_environment(self):
        self._resourcegroup = self.az_get_resource_group(self.config["resource_group"])
        if self._resourcegroup == None:
            self._resourcegroup = self.az_create_resource_group(self.config["resource_group"], self.config["location"])

        self._storageaccount = self.az_get_storage_account(self.config["storage_account_name"])
        if self._storageaccount == None:
            self._storageaccount = self.az_create_storage_account(self.config["storage_account_name"])

        self.import_key(self.ssh_config)

        self._image = self.az_get_image(self.config["image_name"])
        if self._image == None:
            self._image = self.upload_image()


    def upload_image(self, progress_function = None):
        if "image" in self.config:
            image_file = self.config["image"]
            image_name = self.config["image_name"]

            try:
                self.sclient.blob_containers.create(
                    resource_group_name = self._resourcegroup.name,
                    account_name = self._storageaccount.name,
                    container_name = 'vhds',
                    blob_container = {
                        'public_access': 'None'
                    }
                )
            except ResourceExistsError:
                pass

            storage_keys = self.sclient.storage_accounts.list_keys(resource_group_name=self._resourcegroup.name, account_name=self._storageaccount.name)
            keys = {v.key_name: v.value for v in storage_keys.keys}

            connection_string = f"DefaultEndpointsProtocol=https;AccountName={self._storageaccount.name};AccountKey={keys['key1']};EndpointSuffix=core.windows.net"
            blob_client = BlobClient.from_connection_string(
                conn_str=connection_string,
                container_name = 'vhds',
                blob_name = f"{image_name}.vhd",
            )

            chunksize = 4 * 1024 * 1024
            offset = 0
            o = urlparse(image_file)

            if o.scheme == "file":
                image_file = o.path
                file_size = os.path.getsize(image_file)
                blob_client.create_page_blob(file_size)
                self.logger.info(f"Uploading {image_file} ({file_size} bytes) - this may take a while...")

                with open(image_file, 'rb') as f:

                    while offset < file_size:
                        data = f.read(chunksize)
                        remaining = file_size - offset
                        actual_cp_bytes = min(chunksize, remaining)

                        blob_client.upload_page(
                            page=data,
                            offset=offset,
                            length=actual_cp_bytes,
                        )
                        offset += actual_cp_bytes
                        if progress_function:
                            progress_function(total=file_size, uploaded=offset)

            elif o.scheme == "s3":
                s3_url = f"https://{o.hostname}.s3.eu-central-1.amazonaws.com/{o.path.lstrip('/')}"
                meta = urlopen(s3_url)
                file_size = int(meta.getheader('Content-Length'))
                blob_client.create_page_blob(file_size)
                self.logger.info(f"Uploading image from {s3_url} ({file_size} bytes) - this may take a while...")

                while offset < file_size:
                    remaining = file_size - offset
                    actual_cp_bytes = min(chunksize, remaining)

                    blob_client.upload_pages_from_url(
                        source_url=s3_url,
                        offset=offset,
                        length=actual_cp_bytes,
                        source_offset=offset,
                    )
                    offset += actual_cp_bytes
                    if progress_function:
                        progress_function(total=file_size, uploaded=offset)

            image_uri = f"https://{self._storageaccount.name}.blob.core.windows.net/vhds/{image_name}.vhd"

            result = self.cclient.images.begin_create_or_update(
                resource_group_name = self._resourcegroup.name,
                image_name = image_name,
                parameters = {
                    'location': self._resourcegroup.location,
                    'hyper_v_generation': 'V1',
                    'storage_profile': {
                        'os_disk': {
                            'os_type': 'Linux',
                            'os_state': 'Generalized',
                            'blob_uri': image_uri,
                            'caching': 'ReadWrite',
                        }
                    },
                    'tags': self._tags
                }
            ).result()

            self.logger.info(f"Image {image_file} uploaded as {image_name}")
            return result
        else:
            raise Exception("No image with name %s available and no image file given" % self.config["image_name"])


    def import_key(self, config):
        self._ssh_key = self.az_get_ssh_key(config["ssh_key_name"])
        if self._ssh_key == None:
            self._ssh_key = self.az_upload_ssh_key(config["ssh_key_name"], config["ssh_key_filepath"])

    def create_vm(self, config):
        self._nsg = self.az_get_nsg(config["nsg_name"])
        if self._nsg == None:
            self._nsg = self.az_create_nsg(config["nsg_name"])
        self._instance = self.az_create_vm(f"vm-{self.test_name}")
        self.logger.info(f"VM {self._instance.name} created with IP {self._ipaddress.ip_address}")
        return (self._instance, self._ipaddress)
