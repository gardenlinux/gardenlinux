import logging
import json
import os
import uuid
import pytest
import enum

import botocore.client

from os import path
from urllib.parse import urlparse

from . import util

from botocore.exceptions import ClientError

from helper.sshclient import RemoteClient
from paramiko import RSAKey


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TaskStatus(enum.Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    DELETED = 'deleted' # indicates an error (image was rejected)

def response_ok(response: dict):
    resp_meta = response['ResponseMetadata']
    if (status_code := resp_meta['HTTPStatusCode']) == 200:
        return response

    raise RuntimeError(f'rq {resp_meta["RequestId"]=} failed {status_code=}')

def register_image(
    ec2_client: 'botocore.client.EC2',
    snapshot_id: str,
    image_name: str,
    architecture: str,
) -> str:
    '''
    @return: ami-id of registered image
    '''
    root_device_name = '/dev/xvda'

    result = ec2_client.register_image(
        # ImageLocation=XX, s3-url?
        Architecture=architecture,
        BlockDeviceMappings=[
            {
                'DeviceName': root_device_name,
                'Ebs': {
                    'DeleteOnTermination': True,
                    'SnapshotId': snapshot_id,
                    'VolumeType': 'gp2',
                }
            }
        ],
        Description='gardenlinux',
        EnaSupport=True,
        Name=image_name,
        RootDeviceName=root_device_name,
        VirtualizationType='hvm' # | paravirtual
    )

    ec2_client.create_tags(
        Resources=[
            result['ImageId'],
        ],
        Tags=[
            {
                'Key': 'sec-by-def-public-image-exception',
                'Value': 'enabled',
            },
        ]
    )

    # XXX need to wait until image is available (before publishing)
    return result['ImageId']

def import_snapshot(
    ec2_client: 'botocore.client.EC2',
    s3_bucket_name: str,
    image_key: str,
) -> str:
    '''
    @return import_task_id (use for `wait_for_snapshot_import`)
    '''
    res = ec2_client.import_snapshot(
        ClientData={
            'Comment': 'uploaded by gardenlinux-cicd',
        },
        Description='uploaded by gardenlinux-cicd',
        DiskContainer={
            'UserBucket': {
                'S3Bucket': s3_bucket_name,
                'S3Key': image_key,
            },
            'Format': 'raw',
            'Description': 'uploaded by gardenlinux-cicd',
        },
        Encrypted=False,
    )

    import_task_id = res['ImportTaskId']
    return import_task_id


def wait_for_snapshot_import(
    ec2_client: 'botocore.client.EC2',
    snapshot_task_id: str,
    polling_interval_seconds: int=15,
):
    '''
    @return snapshot_id
    '''
    def describe_import_snapshot_task():
        status = ec2_client.describe_import_snapshot_tasks(
            ImportTaskIds=[snapshot_task_id]
        )['ImportSnapshotTasks'][0]
        return status

    def current_status() -> TaskStatus:
        status = describe_import_snapshot_task()
        status = TaskStatus(status['SnapshotTaskDetail']['Status'])
        return status

    def snapshot_id():
        status = describe_import_snapshot_task()
        task_id = status['SnapshotTaskDetail']['SnapshotId']
        return task_id

    while not (status := current_status()) is TaskStatus.COMPLETED:
        logger.info(f'{snapshot_task_id=}: {status=}')

        if status is TaskStatus.DELETED:
            status = describe_import_snapshot_task()
            details = status['SnapshotTaskDetail']
            raise RuntimeError(f'image uploaded by {snapshot_task_id=} was rejected: {details=}')
        time.sleep(polling_interval_seconds)

    return snapshot_id()

class AWS:
    """Handle resources in AWS cloud"""

    @classmethod
    def fixture(cls, session, config, image, test_name) -> RemoteClient:
        AWS.validate_config(config, test_name, image)

        logger.info(f"Using security group {config['securitygroup_name']}")

        aws = AWS(config, session, test_name)
        instance = aws.create_vm(image)
        ssh = None
        try:
            ssh = RemoteClient(
                host=instance.public_dns_name,
                sshconfig=config["ssh"],
                sudo=True
            )
            yield ssh
        finally:
            if ssh is not None:
                ssh.disconnect()
            if aws is not None:
                aws.cleanup_test_resources()

    @classmethod
    def validate_config(cls, cfg: dict, test_name: str, image: str):
        if not 'region' in cfg:
            pytest.exit("AWS region not specified, cannot continue.", 1)
        if not image and not 'ami_id' in cfg and not 'image' in cfg:
            pytest.exit("Neither 'image' nor 'ami_id' specified, cannot continue.", 2)
        if not 'instance_type' in cfg:
            cfg['instance_type'] = "t3.micro"
        if not 'architecture' in cfg or cfg['architecture'] == "amd64":
            cfg['architecture'] = "x86_64"
        if not 'boot_mode' in cfg:
            cfg['boot_mode'] = ""
        if not 'uefi_data' in cfg:
            cfg['uefi_data'] = ""
        if not 'bucket' in cfg:
            cfg['bucket'] = f"img-{test_name}-upload"
        if not 'securitygroup_name' in cfg:
            cfg['securitygroup_name'] = f"{test_name}-sg"
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
        if not 'key_name' in cfg['ssh']:
            cfg['ssh']['key_name'] = f"key-{test_name}"
        if not 'user' in cfg['ssh']:
            cfg['ssh']['user'] = "admin"


    def tags_equal(self, tags1, tags2 = None):
        if not tags2:
            tags2 = self._tags
        t1 = {t['Key']: t['Value'] for t in tags1}
        t2 = {t['Key']: t['Value'] for t in tags2}
        self.logger.debug(f"Test tags: {t2}, resource tags: {t1}")
        return t1 == t2

    def aws_set_ec2_resource_tags(self, id: str):
        resp = response_ok(self.ec2_client.create_tags(
            Resources = [id],
            Tags = self._tags
        ))

    def aws_get_ec2_resource_tags(self, id: str):
        res = response_ok(self.ec2_client.describe_tags(
            Filters=[{
                'Name': 'resource-id',
                'Values': [id]
            }]
        ))
        return res['Tags']


    def aws_get_default_vpcs(self):
        """Get list of default VPCs"""
        response = response_ok(self.ec2_client.describe_vpcs(
            Filters=[{
                "Name": "isDefault",
                "Values": ["true"]
            }]
        ))
        return response['Vpcs']


    def aws_get_security_group(self, name: str):
        resp = response_ok(self.ec2_client.describe_security_groups(
            Filters=[{
                'Name': 'group-name',
                'Values': [name],
            }],
        ))

        if len(resp['SecurityGroups']) > 0:
            return resp['SecurityGroups'][0]['GroupId']
        else:
            return None

    def aws_create_security_group(self, name: str, vpc_id: str = None):
        """Create AWS security group allowing ssh access on port 22."""

        if not vpc_id:
            vpc_id = self.aws_get_default_vpcs()[0]['VpcId']

        self.logger.info(f"Creating security group {name} for VPC {vpc_id}...")
        sg_tags = self._tags.copy()
        sg_tags.append({'Key': 'sec-by-def-network-exception', 'Value': 'SSH'})
        security_group = response_ok(self.ec2_client.create_security_group(
            GroupName = name,
            VpcId = vpc_id,
            Description="allow incoming SSH access",
            TagSpecifications = [{
                'ResourceType': 'security-group',
                'Tags': sg_tags
            }],
        ))
        security_group_id = security_group['GroupId']

        my_ip = util.get_my_ip()
        self.logger.info(f"Enabling incoming SSH connections from {my_ip} to security group {security_group_id}...")
        rule = response_ok(self.ec2_client.authorize_security_group_ingress(
            GroupId = security_group['GroupId'],
            IpPermissions=[
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,         # note, this is not the port to connection comes from but the first port in a range of allowed ports...
                    "ToPort": 22,           # ... and likewise, this is the last port in the range of allowed ports
                    "IpRanges": [
                        {
                            "CidrIp": f"{my_ip}/32",
                            "Description": "Garden Linux test runner"
                        }
                    ],
                }
            ],
            TagSpecifications = [{
                'ResourceType': 'security-group-rule',
                'Tags': sg_tags
            }],
        ))

        return security_group_id

    def aws_delete_security_group(self, group_id: str, force: bool = False):
        tags = self.aws_get_ec2_resource_tags(group_id)
        sg_tags = self._tags.copy()
        sg_tags.append({'Key': 'sec-by-def-network-exception', 'Value': 'SSH'})
        if self.tags_equal(tags, sg_tags) or force:
            self.logger.info(f"Deleting security group with {group_id=}...")
            self.ec2_client.delete_security_group(GroupId=group_id)
        else:
            self.logger.info(f"Keeping security group with {group_id=} as it was not created by this test.")


    def aws_get_ssh_key(self, name: str):
        resp = response_ok(self.ec2_client.describe_key_pairs(
            Filters=[{
                'Name': 'key-name',
                'Values': [name],
            }],
        ))

        if len(resp['KeyPairs']) > 0:
            return resp['KeyPairs'][0]['KeyPairId']
        else:
            return None

    def aws_get_ssh_key_name(self, keypair_id: str):
        resp = response_ok(self.ec2_client.describe_key_pairs(
            Filters=[{
                'Name': 'key-pair-id',
                'Values': [keypair_id],
            }],
        ))
        if len(resp['KeyPairs']) > 0:
            return resp['KeyPairs'][0]['KeyName']
        else:
            return None

    def aws_upload_ssh_key(self, name: str, filepath: str):
        keydata = RSAKey.from_private_key_file(os.path.abspath(filepath))
        pubkey = keydata.get_name() + " " + keydata.get_base64()

        self.logger.info(f"Creating SSH key {name}...")
        resp = response_ok(self.ec2_client.import_key_pair(
            KeyName = name,
            PublicKeyMaterial = pubkey,
            TagSpecifications = [{
                'ResourceType': 'key-pair',
                'Tags': self._tags
            }],
        ))
        return resp['KeyPairId']

    def aws_delete_ssh_key(self, keypair_id: str, force: bool = False):
        tags = self.aws_get_ec2_resource_tags(keypair_id)

        if self.tags_equal(tags, self._tags) or force:
            self.logger.info(f"Deleting SSH keypair with {keypair_id=}...")
            self.ec2_client.delete_key_pair(KeyPairId = keypair_id)
        else:
            self.logger.info(f"Keeping SSH keypair with {keypair_id=} as it was not created by this test.")


    def aws_get_storage_bucket(self, name: str):
        def _check_bucket_region():
            self.logger.debug(f"Checking if bucket is in region {self.session.region_name}")
            resp = response_ok(self.s3_client.get_bucket_location(Bucket = name))
            if resp['LocationConstraint'] == self.session.region_name:
                return True
            return False

        self.logger.debug(f"Checking if S3 bucket {name} exists")
        resp = response_ok(self.s3_client.list_buckets())
        for i in resp['Buckets']:
            if i['Name'] == name and _check_bucket_region():
                return i['Name']
        return None

    def aws_create_storage_bucket(self, name: str):
        self.logger.info(f"Creating S3 storage bucket {name}...")
        resp = self.s3_client.create_bucket(
            Bucket = name,
            CreateBucketConfiguration = {
                'LocationConstraint': self.session.region_name,
            },
            ACL = 'private',
        )

        resp = self.s3_client.put_bucket_tagging(
            Bucket = name,
            Tagging = {
                'TagSet': self._tags
            },
        )

        self.logger.info(f"Setting access policies on storage bucket {name}...")
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [f"arn:aws:s3:::{name}", f"arn:aws:s3:::{name}/*"],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        }
                    }
                },
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": [
                        "s3:GetBucketLocation",
                        "s3:GetObject",
                        "s3:PutObject"
                    ],
                    "Resource": [f"arn:aws:s3:::{name}", f"arn:aws:s3:::{name}/*"],
                }
            ]
        }

        resp = self.s3_client.put_bucket_policy(
            Bucket = name,
            Policy=json.dumps(policy)
        )

        resp = self.s3_client.put_public_access_block(
            Bucket = name,
            PublicAccessBlockConfiguration = {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True,
            },
        )

        self.logger.info(f"Setting server side encryption on storage bucket {name}...")
        encryption_configuration = {
            'Rules': [
                {
                    'ApplyServerSideEncryptionByDefault': {
                        'SSEAlgorithm': 'AES256'
                    },
                    'BucketKeyEnabled': False
                }
            ]
        }

        resp = self.s3_client.put_bucket_encryption(
            Bucket = name,
            ServerSideEncryptionConfiguration = encryption_configuration
        )

        return name

    def aws_delete_storage_bucket(self, name: str, force: bool = False):
        try:
            tags = self.s3_client.get_bucket_tagging(Bucket = name)['TagSet']
        except ClientError:
            if not force:
                self.logger.info(f"Keeping S3 storage bucket {name} as it has no tags attached.")
                return

        if self.tags_equal(tags, self._tags) or force:
            self.logger.info(f"Deleting S3 storage bucket {name}...")
            resp = self.s3_client.delete_bucket(
                Bucket = name,
            )
        else:
            self.logger.info(f"Keeping S3 storage bucket {name} as it was not created by this test.")

    def aws_delete_storage_object(self, bucket: str, key: str, force: bool = False):
        try:
            tags = self.s3_client.get_object_tagging(Bucket=bucket, Key=key)['TagSet']
        except ClientError:
            if not force:
                self.logger.info(f"Keeping S3 object {key} in bucket {bucket} as it has no tags attached.")
                return

        if self.tags_equal(tags, self._tags) or force:
            self.logger.info(f"Deleting S3 object {key} in bucket {bucket}...")
            resp = self.s3_client.delete_object(
                Bucket = bucket,
                Key = key
            )
        else:
            self.logger.info(f"Keeping S3 object {key} in bucket {bucket} as it was not created by this test.")


    def aws_get_ami(self, name: str):
        images = response_ok(self.ec2_client.describe_images(
            Filters=[{
                "Name": "name",
                "Values": [name]
           }]
        ))

        if len(images['Images']) > 0:
            return images['Images'][0]['ImageId']

    def aws_delete_ami(self, ami_id: str, force: bool = False):
        tags = self.aws_get_ec2_resource_tags(ami_id)
        ami_tags = self._tags.copy()
        ami_tags.append({'Key': 'sec-by-def-public-image-exception', 'Value': 'enabled'})
        if self.tags_equal(tags, ami_tags) or force:
            self.logger.info(f"Deleting ami with {ami_id=}...")
            self.ec2_client.deregister_image(ImageId = ami_id)
        else:
            self.logger.info(f"Keeping ami with {ami_id=} as it was not created by this test.")


    def aws_delete_snapshot(self, snapshot_id: str, force: bool = False):
        tags = self.aws_get_ec2_resource_tags(snapshot_id)
        snapshot_tags = self._tags.copy()
        snapshot_tags.append({'Key': 'sec-by-def-ebs-encryption-exception', 'Value': 'enabled'})
        if self.tags_equal(tags, snapshot_tags) or force:
            self.logger.info(f"Deleting snapshot with {snapshot_id=}...")
            self.ec2_client.delete_snapshot(SnapshotId = snapshot_id)
        else:
            self.logger.info(f"Keeping snapshot with {snapshot_id=} as it was not created by this test.")


    def __init__(self, config, session, test_name):
        """
        Create instance of AWS class

        :param config: configuration
        """

        self.config = config
        self.ssh_config = config["ssh"]
        self.test_name = test_name
        self.test_uuid = str(uuid.uuid4())

        self._tags = [
            {"Key": "component", "Value": "gardenlinux"},
            {"Key": "test-type", "Value": "integration-test"},
            {"Key": "test-name", "Value": self.test_name},
            {"Key": "test-uuid", "Value": self.test_uuid}
        ]

        self.session = session

        self.ec2_client = self.session.client("ec2")
        self.s3_client = self.session.client("s3")
        self.ec2_resource = self.session.resource("ec2")

        self.logger = logging.getLogger('aws-testbed')
        self.logger.setLevel(logging.DEBUG)
        self.logger.info(f"This test's tags are:")
        for tag in self._tags:
            self.logger.info(f"\t{tag['Key']}: {tag['Value']}")

        self._storage_bucket_name = None

        self._security_group_id = None
        self._ssh_key_id = None
        self._image_key = None
        self._snapshot_id = None
        self._ami_id = None

        self._instance = None
        self.instance_type = config["instance_type"]


    def __del__(self):
        """Cleanup resources held by this object"""
        self.cleanup_test_resources()


    def cleanup_test_resources(self):
        if "keep_running" in self.config and self.config['keep_running'] == True:
            self.logger.info(f"Keeping all resources alive as requested.")
            return
        if self._instance:
            self.terminate_vm(self._instance)
            self._instance = None
        if self._ssh_key_id:
            self.aws_delete_ssh_key(self._ssh_key_id)
            self._ssh_key_id = None
        if self._security_group_id:
            self.aws_delete_security_group(self._security_group_id)
            self._security_group_id = None
        if self._ami_id:
            self.aws_delete_ami(self._ami_id)
            self._ami_id = None
        if self._snapshot_id:
            self.aws_delete_snapshot(self._snapshot_id)
            self._snapshot_id = None
        if self._image_key:
            self.aws_delete_storage_object(self._storage_bucket_name, self._image_key)
            self._image_key = None
        if self._storage_bucket_name:
            self.aws_delete_storage_bucket(self._storage_bucket_name)
            self._storage_bucket_name = None


    def upload_image(self, image_url):
        image_name = f"img-{self.test_name}"

        if 'ami_id' in self.config:
            ami_id = self.aws_get_ami(self.config['ami_id'])
            self.logger.info(f"Using image with {ami_id=} for this test.")
            return ami_id

        o = urlparse(image_url)

        if o.scheme == "file":
            if not self.aws_get_storage_bucket(self.config["bucket"]):
                self.aws_create_storage_bucket(self.config["bucket"])
            self._storage_bucket_name = self.config['bucket']
            self._image_key = f"{image_name}-{os.path.basename(o.path)}"

            image_key = self._image_key
            bucket_name = self._storage_bucket_name
            self.logger.info(f"Uploading local image {o.path} to S3 storage bucket {bucket_name} - this might take a while...")
            with open(o.path, 'rb') as f:
                self.s3_client.upload_fileobj(Fileobj = f, Bucket = bucket_name, Key = image_key)

            resp = response_ok(self.s3_client.put_object_tagging(
                Bucket = bucket_name,
                Key = image_key,
                Tagging = {
                    'TagSet': self._tags
                },
            ))

            response = self.s3_client.put_object_acl(
                ACL = 'bucket-owner-full-control',
                Bucket = bucket_name,
                Key = image_key,
            )
        elif o.scheme == "s3":
            bucket_name = o.netloc
            image_key = o.path.lstrip("/")
        else:
            raise NotImplementedError("Only local image file uploads and S3 buckets are implemented.")

        self.logger.info(f"Importing snapshot from S3 object {image_key} in bucket {bucket_name}...")
        snapshot_task_id = import_snapshot(
            ec2_client = self.ec2_client,
            s3_bucket_name = bucket_name,
            image_key = image_key,
        )
        try:
            self._snapshot_id = wait_for_snapshot_import(
                ec2_client = self.ec2_client,
                snapshot_task_id = snapshot_task_id,
            )
        except RuntimeError as r:
            import_task = self.ec2_client.describe_import_snapshot_tasks(ImportTaskIds=[snapshot_task_id])
            import_error = import_task['ImportSnapshotTasks'][0]['SnapshotTaskDetail']['StatusMessage']
            logger.error(f"Failed to import snapshot: {import_error}.")
            self.cleanup_test_resources
            raise RuntimeError(f"Failed to import snapshot: {import_error}.")

        snapshot_tags = self._tags.copy()
        snapshot_tags.append({'Key': 'sec-by-def-ebs-encryption-exception', 'Value': 'enabled'})
        self.ec2_client.create_tags(
            Resources = [self._snapshot_id],
            Tags = snapshot_tags,
        )

        self.logger.info(f"Registering ami from snapshot {self._snapshot_id}...")
        self._ami_id = register_image(
            ec2_client = self.ec2_client,
            snapshot_id = self._snapshot_id,
            image_name = image_name,
            architecture = self.config["architecture"],
            boot_mode = self.config["boot_mode"],
            uefi_data = self.config["uefi_data"]
        )
        self.ec2_client.create_tags(
            Resources = [self._ami_id],
            Tags = self._tags
        )

        self.logger.info(f"Image id is {self._ami_id}")
        return self._ami_id

    def create_instance(self, name: str, ami_id: str, disk_size: int = 7, disk_type: str = 'gp3'):
        """Create AWS instance from given AMI and with given security group."""
        ssh_key_filepath = path.expanduser(self.ssh_config["ssh_key_filepath"])

        self._ssh_key_id = self.aws_get_ssh_key(name = self.ssh_config['key_name'])
        if not self._ssh_key_id:
            self._ssh_key_id = self.aws_upload_ssh_key(self.ssh_config['key_name'], ssh_key_filepath)

        instance_tags = self._tags.copy()
        instance_tags.append({'Key': 'Name', 'Value': name})

        volume_tags = self._tags.copy()
        volume_tags.append({'Key': 'sec-by-def-ebs-encryption-exception', 'Value': 'enabled'})

        instance = self.ec2_resource.create_instances(
            BlockDeviceMappings=[
                {
                    "DeviceName": "/dev/xvda",
                    "VirtualName": "string",
                    "Ebs": {
                        "DeleteOnTermination": True,
                        "VolumeSize": disk_size,
                        "VolumeType": disk_type,
                        "Encrypted": False,
                    },
                }
            ],
            ImageId=ami_id,
            InstanceType=self.instance_type,
            KeyName=self.aws_get_ssh_key_name(self._ssh_key_id),
            MaxCount=1,
            MinCount=1,
            SecurityGroupIds=[self._security_group_id],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": instance_tags
                },
                {
                    "ResourceType": "volume",
                    "Tags": volume_tags
                },
            ],
        )
        return instance[0]

    def create_vm(self, image):
        """
        Create an AWS ec2 instance
        - according to the config passed to the constructor
        - enable ssh access

        :returns: instance) to enable cleanup
        """
        self._security_group_id = self.aws_get_security_group(name = self.config['securitygroup_name'])
        if not self._security_group_id:
            self._security_group_id = self.aws_create_security_group(self.config['securitygroup_name'])
        self.logger.info(f"Security group id is {self._security_group_id}")

        if not "ami_id" in self.config:
            ami_id = self.upload_image(image)
            self.config["ami_id"] = ami_id

        self._instance = self.create_instance(self.test_name, ami_id=self.config['ami_id'])

        self._instance.wait_until_exists()
        self._instance.reload()

        self.logger.info(f"Created {self._instance} from ami {self.config['ami_id']}, waiting for start...")

        self._instance.wait_until_running()
        self._instance.reload()
        self.logger.info(f"Instance {self._instance} is running, waiting for status checks...")

        waiter = self.ec2_client.get_waiter("instance_status_ok")
        waiter.wait(InstanceIds=[self._instance.id])
        self.logger.info(f"Status checks of {self._instance} succeeded.")
        self.logger.info(f"Ec2 instance is accessible through {self._instance.public_dns_name}")

        return self._instance

    def terminate_vm(self, instance):
        """Stop and terminate the given ec2 instance"""
        instance.terminate()
        self.logger.info(f"Terminating ec2 instance {instance}...")
        instance.wait_until_terminated()
        instance.reload()
        self.logger.info(f"Terminated ec2 instance {instance}")
        return instance
