import datetime
import logging
from os import path

import boto3

from .sshclient import RemoteClient

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class AWS:
    """Handle resources in AWS cloud"""

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

    def create_vm(self):
        """
        Create an AWS ec2 instance
        - according to the config passed to the constructor
        - enable ssh access

        :returns: instance) to enable cleanup
        """
        self.security_group_id = self.create_security_group(
            group_name="gardenlinux-test"
        )
        self.instance = self.create_instance()

        self.instance.wait_until_exists()
        self.instance.reload()

        ami_id = self.config["ami_id"]
        logger.info(f"created {self.instance} from ami {ami_id}, waiting for start ...")

        self.instance.wait_until_running()
        self.instance.reload()
        logger.info(f"{self.instance} is running, waiting for status checks ...")

        waiter = self.client.get_waiter("instance_status_ok")
        waiter.wait(InstanceIds=[self.instance.id])
        logger.info(f"status checks of {self.instance} succeeded")

        return self.instance

    def terminate_vm(self, instance):
        """Stop and terminate the given ec2 instance"""
        instance.terminate()
        logger.info("terminating ec2 instance {instance} ...")
        instance.wait_until_terminated()
        instance.reload()
        logger.info(f"terminated ec2 instance {instance}")
        return instance
