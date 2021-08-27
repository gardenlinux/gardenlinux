import datetime
import logging
import json
import sys
import subprocess
from os import path

from .sshclient import RemoteClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Azure:
    """Handle resources in Azure cloud"""

    @classmethod
    def fixture(cls, config) -> RemoteClient:
        aws = AWS(config)
        instance = aws.create_vm()
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
            if aws is not None:
                aws.__del__()

    def __init__(self, config):
        """
        Create instance of AWS class

        :param config: configuration
        """
        self.config = config
        if (
            self.config["access_key_id"]
            and self.config["secret_access_key"]
            and self.config["region"]
        ):
            self.session = boto3.Session(
                aws_access_key_id=self.config["access_key_id"],
                aws_secret_access_key=self.config["secret_access_key"],
                region_name=self.config["region"],
            )
        elif self.config["region"]:
            self.session = boto3.Session(region_name=self.config["region"])
        else:
            self.session = boto3.Session()
        self.client = self.session.client("ec2")
        self.ec2 = self.session.resource("ec2")
        self.security_group_id = None
        self.instance = None
        self.instance_type = config["instance_type"]


    def __del__(self):
        """Cleanup resources held by this object"""
        if self.instance:
            self.terminate_vm(self.instance)
            self.instance = None
        if self.security_group_id:
            self.delete_security_group((self.security_group_id))
            self.security_group_id = None

    def get_default_vpcs(self):
        """Get list of default VPCs"""
        response = self.client.describe_vpcs(
            Filters=[{"Name": "isDefault", "Values": ["true"],}]
        )
        vpcs = [v["VpcId"] for v in response["Vpcs"]]
        return vpcs

    def find_key(self, name) -> bool:
        """
        Find ssh key with given name.

        :param name: name of the key uploaded to AWS
        :returns: the key if it exists
        """
        response = self.client.describe_key_pairs()
        try:
            found = next(k for k in response["KeyPairs"] if k["KeyName"] == name)
        except StopIteration:
            found = None
        logger.info(f"found ssh key {name}: {found}")
        return found

    def import_key(self, key_name, ssh_key_filepath):
        """
        Import a public ssh key to AWS

        :param key_name: name of the key
        :param ssh_key_filepath: path of the private key in the local filesystem
        """
        with open(f"{ssh_key_filepath}.pub", "rb") as f:
            public_key_bytes = f.read()
            response = self.client.import_key_pair(
                KeyName=key_name, PublicKeyMaterial=public_key_bytes,
            )
            fingerprint = response["KeyFingerprint"]
            logger.info(f"imported key-pair {key_name} with fingerprint {fingerprint}")

    def find_security_group(self, name):
        """
        Find a security group by name and return its id

        :param name: name of the security group
        :returns: the group id of the security group
        """
        response = self.client.describe_security_groups(
            Filters=[{"Name": "group-name", "Values": [name,]}]
        )
        groups = response.get("SecurityGroups")
        if not groups:
            return
        group_id = groups[0].get("GroupId")
        logger.info(f"found {group_id=}")
        return group_id

    def create_security_group(self, group_name):
        """Create AWS security group allowing ssh access on port 22."""
        vpcs = self.get_default_vpcs()
        vpc_id = vpcs[0]
        logger.info(f"default vpc: {vpc_id=}")
        security_group_id = self.find_security_group(group_name)
        if not security_group_id:
            logger.info("security group %s doesn't exist -> create it" % group_name)
            security_group = self.ec2.create_security_group(
                GroupName=group_name,
                Description=f"{group_name} allowing ssh access",
                VpcId=vpc_id,
            )
            security_group_id = security_group.id
            logger.info(f"security group created {security_group_id} in vpc {vpc_id}.")

            self.client.authorize_security_group_ingress(
                GroupId=security_group_id,
                IpPermissions=[
                    {
                        "IpProtocol": "tcp",
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpRanges": [{"CidrIp": "0.0.0.0/1"}, {"CidrIp": "128.0.0.0/1"}],
                    }
                ],
            )
            logger.info("ingress successfully set")
        else:
            logger.info(
                f"security group {group_name} already exists with id {security_group_id}"
            )
        return security_group_id

    def delete_security_group(self, security_group_id):
        """Delete the given security group, must not be referenced anymore"""
        try:
            self.client.delete_security_group(GroupId=security_group_id)
            logger.info(f"deleted security group {security_group_id=}")
        except boto3.exceptions.Boto3Error as e:
            logger.exception(e)

    def create_instance(self):
        """Create AWS instance from given AMI and with given security group."""
        ami_id = self.config["ami_id"]
        key_name = self.config["key_name"]
        ssh_key_filepath = path.expanduser(self.config["ssh_key_filepath"])
        logger.debug("ssh_key_filepath: %s" % ssh_key_filepath)

        if not ssh_key_filepath:
            ssh_key_filepath = "gardenlinux-test"
        if not (
            path.exists(ssh_key_filepath) and path.exists(f"{ssh_key_filepath}.pub")
        ):
            passphrase = self.config["passphrase"]
            user = self.config["user"]
            RemoteClient.generate_key_pair(ssh_key_filepath, 2048, passphrase, user)
        if not self.find_key(key_name):
            self.import_key(key_name, ssh_key_filepath)

        name = f"gardenlinux-test-{ami_id}-{datetime.datetime.now().isoformat()}"
        instance = self.ec2.create_instances(
            BlockDeviceMappings=[
                {
                    "DeviceName": "/dev/xvda",
                    "VirtualName": "string",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "VolumeSize": 3,
                        "VolumeType": "standard",
                        "Encrypted": False,
                    },
                }
            ],
            ImageId=ami_id,
            InstanceType=self.instance_type,
            KeyName=key_name,
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=[self.security_group_id,],
            TagSpecifications=[
                {"ResourceType": "instance", "Tags": [{"Key": "Name", "Value": name}]}
            ],
        )
        return instance[0]


    def create_vm_cmd(self, image, name, resource_group, admin_username, nsg, ssh_key_name, size):
        cmd = [ "az", "vm", "create", "--image", image, "--name", name, "--resource-group", resource_group, "--admin-username", admin_username, "--nsg", nsg, "--ssh-key-name", ssh_key_name, "--size", size]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # todo
            sys.exit("Unable to create vm")
        doc = json.loads(result.stdout)
        return doc["id"]


    def create_nsg_cmd(self, name, resource_group, subscription):
        cmd = ["az", "network", "nsg", "create", "--name", name, "--resource-group", resource_group]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # todo
            sys.exit("Unable to create nsg" + result.stderr)

        cmd = ["az", "network", "nsg", "rule", "create", "--name", "ssh", "--nsg-name", name, "--priority", 300, "--access", "Allow", "--protocol", "Tcp", "--source-address-prefixes", "0.0.0.0/1 128.0.0.0/1", "--subscription", subscription]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            # todo
            sys.exit("Unable to add rule " + result.stderr)


    def create_vm(self):
        """
        Create an Azure vm instance
        - according to the config passed to the constructor
        - enable ssh access

        :returns: instance) to enable cleanup
        """
        self.create_nsg_cmd(self.config["nsg_name"], self.config["resource_group"], self.config["subscription"])
        return self.create_vm_cmd(self.config["image"],"integration-test" ,self.config["resource_group"], "azureuser", self.config["nsg_name"], self.config["ssh_key_name"], "Standard_B1s")

"""
D040949@C02FK1SNMD6T cc-config % az vm create --image /subscriptions/00d2caa5-cd29-46f7-845a-2f8ee0360ef5/resourceGroups/garden-linux/providers/Microsoft.Compute/images/garden-linux-318.6.0 --name inte-test-del-d040949 --resource-group garden-linux --admin-username azureuser --nsg d040949-gl-318.5-nsg --ssh-key-name dirk-test --size Standard_B1s
{
  "fqdns": "",
  "id": "/subscriptions/00d2caa5-cd29-46f7-845a-2f8ee0360ef5/resourceGroups/garden-linux/providers/Microsoft.Compute/virtualMachines/inte-test-del-d040949",
  "location": "westeurope",
  "macAddress": "00-0D-3A-28-0D-AD",
  "powerState": "VM running",
  "privateIpAddress": "10.0.0.11",
  "publicIpAddress": "13.80.172.100",
  "resourceGroup": "garden-linux",
  "zones": ""
}

az vm delete --ids "/subscriptions/00d2caa5-cd29-46f7-845a-2f8ee0360ef5/resourceGroups/garden-linux/providers/Microsoft.Compute/virtualMachines/inte-test-del-d040949" --yes

az network nsg create --name d040949-tmp --resource-group garden-linux

nsg rule create --name ssh --nsg-name d040949-tmp --priority 300 --access Allow --direction Inbound --protocol Tcp --source-address-prefixes 0.0.0.0/1 128.0.0.0/1 --subscription sap-se-az-scp-k8s-dev --resource-group garden-linux

"""


    def terminate_vm(self, instance):
        """Stop and terminate the given ec2 instance"""
        instance.terminate()
        logger.info("terminating ec2 instance {instance} ...")
        instance.wait_until_terminated()
        instance.reload()
        logger.info(f"terminated ec2 instance {instance}")
        return instance
