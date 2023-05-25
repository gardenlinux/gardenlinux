#!/usr/bin/env python3

import argparse
import re
import sys
import time
import logging
import json
import uuid

import boto3

# number of intervals to wait for the snapshot import
# each interval is 5 seconds so the given value of 120 here is 10 minutes
IMPORT_TIMEOUT_INTERVALS = 120

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def response_ok(response: dict):
    resp_meta = response['ResponseMetadata']
    status_code = resp_meta['HTTPStatusCode']
    if (status_code == 200) or (status_code == 204):
        return response

    raise RuntimeError(f'rq {resp_meta["RequestId"]=} failed {status_code=}')


class S3Bucket:

    def __init__(self, s3_client, logger, bucket_name, region_name, tags = None):
        self.s3_client = s3_client
        self.logger = logger
        self.bucket_name = bucket_name
        self.region_name = region_name
        self.tags = tags
        self.created = False

    
    def exists(self):
        def _check_bucket_region():
            self.logger.debug(f"Checking if bucket is in region {self.region_name}")
            resp = response_ok(self.s3_client.get_bucket_location(Bucket = self.bucket_name))
            if resp['LocationConstraint'] == self.region_name:
                return True
            return False

        self.logger.debug(f"Checking if S3 bucket {self.bucket_name} exists")
        resp = response_ok(self.s3_client.list_buckets())
        for i in resp['Buckets']:
            if i['Name'] == self.bucket_name and _check_bucket_region():
                return True
        return False


    def create_storage_bucket(self):
        if self.exists():
            self.logger.warning(f"Storage bucket {self.bucket_name} already exists, not creating...")
            return
        
        self.logger.debug(f"Creating S3 storage bucket {self.bucket_name}...")
        _ = self.s3_client.create_bucket(
            Bucket = self.bucket_name,
            CreateBucketConfiguration = {
                'LocationConstraint': self.region_name,
            },
            ACL = 'private',
        )

        if self.tags != None:
            _ = self.s3_client.put_bucket_tagging(
                Bucket = self.bucket_name,
                Tagging = {
                    'TagSet': self.tags
                },
            )

        self.logger.debug(f"Setting access policies on storage bucket {self.bucket_name}...")
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Deny",
                    "Principal": "*",
                    "Action": "s3:*",
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}", f"arn:aws:s3:::{self.bucket_name}/*"],
                    "Condition": {
                        "Bool": {
                            "aws:SecureTransport": "false"
                        },
                        "NumericLessThan": {
                            "s3:TlsVersion": '1.2'
                        }
                    }
                }
            ]
        }

        _ = self.s3_client.put_bucket_policy(
            Bucket = self.bucket_name,
            Policy=json.dumps(policy)
        )

        self.logger.debug(f"Setting public access block on storage bucket {self.bucket_name}...")
        _ = self.s3_client.put_public_access_block(
            Bucket = self.bucket_name,
            PublicAccessBlockConfiguration = {
                'BlockPublicAcls': True,
                'IgnorePublicAcls': True,
                'BlockPublicPolicy': True,
                'RestrictPublicBuckets': True,
            },
        )

        self.logger.debug(f"Setting server side encryption on storage bucket {self.bucket_name}...")
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

        _ = self.s3_client.put_bucket_encryption(
            Bucket = self.bucket_name,
            ServerSideEncryptionConfiguration = encryption_configuration
        )

        self.created = True
        return self.bucket_name


    def delete_storage_bucket(self, force: bool = False):
        if not (self.created or force):
            self.logger.warning(f"Bucket {self.bucket_name} was created externally and will not be deleted.")
            return
        
        for i in response_ok(self.s3_client.list_objects(Bucket=self.bucket_name))['Contents']:
            self.logger.debug(f"Deleting object s3://{self.bucket_name}/{i['Key']}")
            _ = response_ok(self.s3_client.delete_object(Bucket=self.bucket_name, Key=i['Key']))

        self.logger.debug(f"Deleting S3 bucket s3://{self.bucket_name}")
        _ = response_ok(self.s3_client.delete_bucket(
            Bucket = self.bucket_name,
        ))


class Ec2ImageImport:
    def __init__(self, args):
        self.s3_bucket = args.bucket
        self.s3_key = None
        self.region = args.region
        self.permission = args.permission_public
        self.distribute = args.distribute
        self.raw_image = args.raw_image
        self.image_name = args.image_name
        self.debug = args.debug
        self.purpose = args.purpose
        self.tags = args.tags
        self.profile_name = args.profile_name
        self.architecture = args.architecture
        self.image_overwrite = args.image_overwrite

        if self.debug:
            handler.setLevel(logging.DEBUG)
            logger.setLevel(logging.DEBUG)

        self.boto_session=boto3.Session(profile_name=self.profile_name, region_name=self.region)
        self.s3_client=self.boto_session.client('s3')
        self.ec2_client=self.boto_session.client('ec2')


    def aws_command_prefix(self):
        return ["aws", "--region", self.region, "--output", "json"]


    def upload_image(self):
        logger.debug(f"Checking whether S3 bucket {self.s3_bucket} exists...")

        found = False
        for b in response_ok(self.s3_client.list_buckets()).get('Buckets'):
            if b.get('Name') == self.s3_bucket:
                found = True

        if not found:
            sys.exit(f"Bucket {self.s3_bucket} does not exist.")

        logger.debug("Checking bucket location...")
        locationContraint = self.s3_client.get_bucket_location(Bucket=self.s3_bucket).get('LocationConstraint')
        if locationContraint != self.region:
            sys.exit(f"Bucket {self.s3_bucket} is located in region {locationContraint} but image shall be imported in region {self.region}")
        else:
            logger.debug(f"Bucket is in chosen region {self.region}")

        logger.debug("Checking whether image has already been uplodaded...")

        image_available = False
        try:
            self.s3_client.get_object(Bucket=self.s3_bucket, Key=self.image_name)
            logger.debug(f"Image blob s3://{self.s3_bucket}/{self.image_name} already exists.")
            image_available = True
        except self.s3_client.exceptions.NoSuchKey:
            logger.debug(f"Image blob s3://{self.s3_bucket}/{self.image_name} does not exist.")

        self.s3_key = self.image_name

        if (not image_available) or self.image_overwrite:
            logger.info(f"Uploading to s3://{self.s3_bucket}/{self.image_name}...")
            with open(self.raw_image, 'rb') as image_data:
                self.s3_client.upload_fileobj(Fileobj=image_data, Bucket=self.s3_bucket, Key=self.image_name)
                logger.info(f"Image uploaded to s3://{self.s3_bucket}/{self.image_name}")
            return True
        else:
            logger.info(f"An image blob {self.image_name} already exists in bucket {self.s3_bucket} and image_overwrite set to False. Continuing with the existing image blob.")
            return False


    def import_snapshot(self):
        """A role is required for the import_snapshot operation to succeed, see
        https://docs.aws.amazon.com/snowball/latest/developer-guide/ec2-ami-import-cli.html"""

        resp = response_ok(self.ec2_client.import_snapshot(
            ClientData={
                'Comment': f'image import for {self.image_name}',
            },
            Description=f'image import for {self.image_name}',
            DiskContainer={
                'UserBucket': {
                    'S3Bucket': self.s3_bucket,
                    'S3Key': self.image_name,
                },
                'Format': 'raw',
                'Description': f'image import for {self.image_name}',
            },
            Encrypted=False,
        ))

        import_task_id = resp.get("ImportTaskId")
        status = resp.get("SnapshotTaskDetail").get("Status")
        logger.info(f"Creating Snapshot for {self.image_name}, {import_task_id=}, {status=}")

        snapshot_id = ""

        for _ in range(IMPORT_TIMEOUT_INTERVALS):
            resp = response_ok(self.ec2_client.describe_import_snapshot_tasks(
                ImportTaskIds=[
                    import_task_id,
                ],
            ))

            import_snapshot_task = resp.get('ImportSnapshotTasks')[0]
            task_details = import_snapshot_task["SnapshotTaskDetail"]
            status = task_details['Status']

            if status == "deleted":
                status_message = task_details.get('StatusMessage', 'no detailed message')
                sys.exit(f"Snapshot creation failed with {status_message}")

            if status == "completed":
                snapshot_id = task_details["SnapshotId"]
                break

            time.sleep(5)
        if snapshot_id == "":
            sys.exit("No snapshot_id which means most likely that no snapshot has been created")
        logger.debug(f"Snapshot id {snapshot_id}")

        self.tag_resource(snapshot_id, {'purpose': self.purpose})

        return snapshot_id


    def tag_resource(self, resource_id, tag_specifications):
        for key in tag_specifications:
            logger.debug(f"Tagging resource {resource_id} with {key}:{tag_specifications[key]}")
            response_ok(self.ec2_client.create_tags(
                Resources=[
                    resource_id,
                ],
                Tags=[
                    {
                        'Key': key,
                        'Value': tag_specifications[key],
                    },
                ]
            ))

            logger.debug(f"Resource {resource_id} successfully tagged with {key}:{tag_specifications[key]}")


    def register_image(self, snapshot_id):
        logger.debug(f"Check whether image with name {self.image_name} already exists.")

        resp = response_ok(self.ec2_client.describe_images(
            Owners=[
                'self',
            ],
        ))

        idx = 0
        for i in resp['Images']:
            name = i["Name"]
            if name.startswith(self.image_name):
                if name == self.image_name:
                    idx = max(idx, 1)
                else:
                    m = re.search(r"-(\d+)$", name)
                    if m:
                        idx = max(int(m.group(1)) + 1, idx)

        if idx != 0:
            self.image_name = f"{self.image_name}-{idx}"

        logger.debug(f"Registering image for snapshot {snapshot_id}...")
        resp = response_ok(self.ec2_client.register_image(
            Architecture=self.architecture,
            BlockDeviceMappings=[
                {
                    'DeviceName': '/dev/xvda',
                    'Ebs': {
                        'DeleteOnTermination': True,
                        'SnapshotId': snapshot_id,
                        'VolumeType': 'gp2',
                    },
                },
            ],
            Description='Garden Linux',
            EnaSupport=True,
            Name=self.image_name,
            RootDeviceName='/dev/xvda',
            VirtualizationType='hvm',
            BootMode='uefi-preferred',
        ))

        ami_id = resp['ImageId']
        logger.debug(f"Registered image with AMI ID {ami_id}")

        self.tag_resource(snapshot_id, {'ami-name': self.image_name})
        self.tag_resource(snapshot_id, {'ami-id': ami_id})

        if self.purpose != "":
            self.tag_resource(ami_id, {'purpose': self.purpose})

        if self.tags != "":
            tags=str.split(",")
            for tag in tags:
                kv = tag.split("=")
                self.tag_resource(ami_id, {kv[0]:kv[1]})

        self.tag_resource(ami_id, {'sec-by-def-public-image-exception': 'enabled'})

        return ami_id


    def make_amis_public(self, amis):
        if self.permission == False:
            return

        for region, ami in amis.items():
            logger.debug(f"Making ami {ami} in region {region} public.")

            ec2 = boto3.Session(profile_name=self.profile_name, region_name=region).client('ec2')
            response_ok(ec2.modify_image_attribute(
                ImageId=ami,
                LaunchPermission={
                    'Add': [
                        {
                            'Group': 'all',
                        },
                    ],
                }
            ))


    def distribute_ami(self, src_ami):
        src_region = self.region
        amis = {src_region: src_ami}
        if self.distribute == False:
            return amis

        regions_raw = self.ec2_client.describe_regions()["Regions"]

        for dst_region in list(map(lambda x: x["RegionName"], regions_raw)):
            if dst_region == src_region:
                continue

            ec2 = boto3.Session(profile_name=self.profile_name, region_name=dst_region).client('ec2')

            resp = response_ok(ec2.copy_image(
                Encrypted=False,
                Name=self.image_name,
                SourceImageId=src_ami,
                SourceRegion=src_region,
                CopyImageTags=True,
            ))

            dst_ami = resp["ImageId"]

            self.tag_resource(dst_ami, {'source_ami': src_ami})
            self.tag_resource(dst_ami, {'source_region': src_region})

            amis[dst_region] = dst_ami
        return amis


    def run(self):
        if self.s3_bucket == None:
            self.s3_bucket = f"gardenlinux-import-{str(uuid.uuid4())}"
        self.bucket = S3Bucket(s3_client=self.s3_client, logger=logger, bucket_name=self.s3_bucket, region_name=self.region)
        if not self.bucket.exists():
            self.bucket.create_storage_bucket()
        image_uploaded = self.upload_image()
        snapshot_id = self.import_snapshot()
        self.bucket.delete_storage_bucket()
        ami_id = self.register_image(snapshot_id)
        logging.debug("Got ami_id: " + ami_id)
        amis = self.distribute_ami(ami_id)
        self.make_amis_public(amis)
        result = {
            "s3-blob": {
                "bucket": self.s3_bucket,
                "key": self.s3_key,
                "uploaded": image_uploaded,
            },
            "snapshot-id": snapshot_id,
            "ami-id": ami_id,
            "region": self.region,
            "all-amis": amis,
        }
        print(json.dumps(result, indent=4))

    @classmethod
    def _argparse_register(cls, parser):

        parser.add_argument(
            "--bucket", 
            type=str, 
            dest="bucket", 
            help="Upload bucket"
        )
        parser.add_argument(
            "--permission-public",
            type=bool,
            default=False,
            help="Make snapshot and image public",
        )
        parser.add_argument(
            "--distribute",
            type=bool,
            default=False,
            help="Copy the image across AWS regions",
        )
        parser.add_argument("--region", type=str, help="AWS region", required=True)
        parser.add_argument(
            "--image-name",
            type=str,
            dest="image_name",
            help="Name of image in bucket and snapshot",
            required=True,
        )
        parser.add_argument("raw_image", type=str, help="RAW image file")
        parser.add_argument(
            "--image-overwrite",
            type=bool,
            default=False,
            dest="image_overwrite",
            help="if set, the any given image with the same name in the target bucket will be overwritten",
        )
        parser.add_argument(
            "--purpose",
            type=str,
            default="test-image-import",
            help="purpose of this upload (defaults to test so it can be removed without affecting production",
        )
        parser.add_argument(
            "--tags",
            type=str,
            default="",
            help="additional tags to set in format name=value,name1=value1,..."
        )
        parser.add_argument(
            "--profile_name",
            type=str,
            default=None,
            help="the name of the AWS profie to use (equivalent to AWS_PROFILE_NAME environment variable"
        )
        parser.add_argument(
            "--architecture",
            type=str,
            default='x86_64',
            choices=['x86_64', 'arm64'],
            help="the name of the AWS profie to use (equivalent to AWS_PROFILE_NAME environment variable"        
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="debug"
        )


    @classmethod
    def _main(cls):
        parser = argparse.ArgumentParser()
        cls._argparse_register(parser)
        args = parser.parse_args()

        ec2_img_build = cls(args)
        ec2_img_build.run()


if __name__ == "__main__":
    Ec2ImageImport._main()
