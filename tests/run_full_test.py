#!/usr/bin/env python3

import tempfile
import logging
import argparse
import os
import os.path
import pathlib
import sys
from urllib.parse import urlparse
import subprocess
import selectors
import time
import paramiko

import yaml
import json

import boto3
import botocore
import glci.aws
from azurewrapper import AzureWrapper


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


"""
class GCPFullTest:
    import google.cloud

    def __init__(self, config):
        self.gcp_config = config
        if "service_account_json_path" in self.gcp_config:
            svc_file = pathlib.Path(self.gcp_config["service_account_json_path"])
            if not svc_file.is_file:
                logger.error("Service account json %s does not exist", str(svc_file))

        self.gcs_client = google.cloud.storage.Client.from_service_account_json(str(svc_file))
        self.gce_client = google.cloud.client.Client.from_service_account_json(str(svc_file))
        return
    def upload_ssh_key(self):
        return
    def delete_ssh_key(self):
        return
    def upload_image(self, image_url):
        o = urlparse(image_url)

# not tested, unlikely to work... but we will not get here anyway as GCP is still raising a "not implemented error"
        if o.scheme != "" and o.scheme != "file":
            raise NotImplementedError("Only local image file uploads and S3 buckets are implemented.")
        logger.debug("Uploading image %s" % image_url)
        image_file = o.path
        image_blob_name = "gardenlinux-integration-test-image.tar.gz"
        
        gcp_bucket = self.gcs_client.get_bucket(self.gcp_config["bucket"])
        image_blob = gcp_bucket.blob(image_blob_name)
        image_blob.upload_from_filename(image_file)

        return
    def run_integration_test(self, configfile):
        return
    def delete_image(self):
        return
    def run(self):
        return
"""

class AWSFullTest:

    def __init__(self, config):
        self.aws_config = config
        botoargs={}
        if "access_key_id" in self.aws_config:
            botoargs["aws_access_key_id"] = self.aws_config["access_key_id"]
        if "secret_access_key" in self.aws_config:
            botoargs["aws_secret_access_key"] = self.aws_config["secret_access_key"]
        if "region" in self.aws_config:
            botoargs["region_name"] = self.aws_config["region"]
        self.ec2 = boto3.client('ec2', **botoargs)
        self.s3 = boto3.client('s3', **botoargs)

        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # self.gardenlinux_bin = os.path.join(dir_path, os.pardir, "bin")

    def upload_ssh_key(self):
        response = self.ec2.describe_key_pairs()
        if "KeyPairs" in response:
            for kp in response["KeyPairs"]:
                if kp["KeyName"] == self.aws_config["key_name"]:
                    logger.debug(
                        "public key '%s' already uploaded" % self.aws_config["key_name"]
                    )
                    return

        logger.debug("Uploading public key '%s' " % self.aws_config["key_name"])
        if "ssh_key_filepath" in self.aws_config:
            ssh_key_file_path=self.aws_config["ssh_key_filepath"]
        else:
            sys.exit("SSH keyfile not given in test configuration")
            # TODO: generate a key on the fly
        k = paramiko.RSAKey.from_private_key_file(os.path.abspath(ssh_key_file_path))
        pub = k.get_name() + " " + k.get_base64()
        self.ec2.import_key_pair(
            KeyName=self.aws_config["key_name"],
            PublicKeyMaterial=pub,
            TagSpecifications=[
                {
                    "ResourceType": "key-pair",
                    "Tags": [
                        {"Key": "purpose", "Value": "integration_test"},
                    ],
                },
            ],
        )

    def delete_ssh_key(self):
        self.ec2.delete_delete_key_pair(KeyName=self.config.aws.key_name)

    def upload_image(self, image_url):
        o = urlparse(image_url)
        if o.scheme == "s3":
            image_name="gl-integration-test-image-" + o.path.split("/objects/", 1)[1]
            images = self.ec2.describe_images(Filters=[{
                "Name": "name",
                "Values": [image_name]
            }])
            if len(images['Images']) > 0:
                ami_id = images['Images'][0]['ImageId']
                logger.debug("Image with AMI id %s already exists", ami_id)
                return {"ami-id": ami_id}

            snapshot_task_id = glci.aws.import_snapshot(
                ec2_client=self.ec2,
                s3_bucket_name=o.netloc,
                image_key=o.path.lstrip("/"),
            )
            snapshot_id = glci.aws.wait_for_snapshot_import(
                ec2_client=self.ec2,
                snapshot_task_id=snapshot_task_id,
            )
            initial_ami_id = glci.aws.register_image(
               ec2_client=self.ec2,
               snapshot_id=snapshot_id,
               image_name="gl-integration-test-image-" + o.path.split("/objects/",1)[1],
            )
            logger.debug("Imported image %s as AMI %s", image_url, initial_ami_id)
            return {"ami-id": initial_ami_id}
        if o.scheme != "" and o.scheme != "file":
            raise NotImplementedError("Only local image file uploads and S3 buckets are implemented.")
        logger.debug("Uploading image %s" % image_url)
        image_file = o.path
        cmd = [
            os.path.join(self.repo_root, "bin", "make-ec2-ami"),
            "--bucket",
            self.aws_config["bucket"],
            "--region",
            self.aws_config["region"],
            "--image-name",
            self.aws_config["image_name"],
            "--purpose",
            "integration-test",
            "--image-overwrite",
            "false",
        ]
        if self.debug:
            cmd = cmd + ["--debug"]
        cmd = cmd + [image_file]
        logger.debug("Running command: " + (" ".join([v for v in cmd])))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            sys.exit("Error uploading image %s" % (result.stderr.decode("utf-8")))
        logger.debug("Result of upload_image %s" % (result.stdout.decode("utf-8")))
        return json.loads(result.stdout)

    def run_integration_test(self, configfile):
        logger.info("Starting integration tests")
        cmd = ["pytest", "--iaas=aws", "--configfile=" + configfile, "integration/"]
        logger.debug("Running command: " + " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True, cwd="/gardenlinux/tests")
        logger.info("Integration tests returned with %d" % result.returncode)
        logger.info(result.stdout.decode("utf-8"))
        logger.info(result.stderr.decode("utf-8"))
        if result.returncode == 0:
            return True
        else:
            return False

    def delete_image(self):
        ami_id = self.aws_config["ami_id"]
        image = self.ec2.describe_images(ImageIds=[ami_id])
        snapshot_id = image["Images"][0]["BlockDeviceMappings"][0]["Ebs"]["SnapshotId"]

        # (1) ami
        self.ec2.deregister_image(ImageId=ami_id)

        # (2) snapshot
        self.ec2.delete_snapshot(SnapshotId=snapshot_id)

        # (3) bucket
        # if self.config['image-uploaded'] == True:
        #    self.s3.delete_object(Bucket='%s',Key='%s' % (self.aws_config['bucket'], self.aws_config['image_name']))

    def delete_ssh_key(self):
        self.ec2.delete_key_pair(KeyName=self.aws_config["key_name"])

    def run(self):
        self.upload_ssh_key()
        ami_id = self.aws_config["ami_id"] if "ami_id" in self.aws_config else None
        upload_result = None

        if "image" in self.aws_config:
            # upload an image and test that
            logger.info(
                "Uploading new image %s to AWS for test" % self.aws_config["image"]
            )
            upload_result = self.upload_image(self.aws_config["image"])
            ami_id = upload_result["ami-id"]

        if ami_id == None:
            logger.error("No imge or ami_id specifified")
            os.exit(1)

        self.new_config_file = "/tmp/test_config_amended.yaml"
        if upload_result is not None:
            self.aws_config["ami_id"] = upload_result["ami-id"]
        with open("/tmp/test_config_amended.yaml", "w") as f:
            yaml.dump(self.aws_config, f)

        test_result = self.run_integration_test(self.new_config_file)
        if test_result == True:
            logger.info("Tests successful, deleting image")
            self.delete_image()
            self.delete_ssh_key()
        else:
            logger.info("Tests not successful, instance still running")



class AzureFullTest:

    def __init__(self, config):
        self.config = config
        self.subscription = self.config["subscription"]
        self.resource_group = self.config["resource_group"]
        self.az = AzureWrapper(self.azure)


    def upload_image(self):
        logger.debug("Uploading image %s" % image_url)
        image_file = o.path
        cmd = [
            os.path.join(self.repo_root, "bin", "make-azure-ami"),
            "--resource-group",
            self.azure_config["resource_group"],
            "--storage-account-name",
            self.azure_config["storage_account_name"],
            "--image-name",
            self.azure_config["image_name"],
            "--image-path",
            self.azure_config["image"]
        ]
        if self.debug:
            cmd = cmd + ["--debug"]
        logger.debug("Running command: " + (" ".join([v for v in cmd])))
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            sys.exit("Error uploading image %s" % (result.stderr.decode("utf-8")))
        logger.debug("Result of upload_image %s" % (result.stdout.decode("utf-8")))


    def delete_image(self):
        raise Excption("not yet implemented")


    def upload_ssh_key(self):
        if self.az.get_ssh_key(self.subscription, self.resource_group, self.config["ssh_key_name"]) == None:
            self.az.upload_ssh_key(self.subscription, self.resource_group, self.config["ssh_key_filepath"], self.config["ssh_key_name"])


    def delte_ssh_key(self):
        self.az.delte_ssh_key(self.subscription, self.resource_group, self.config["ssh_key_name"])

    def run_integration_test(self, configfile):
        logger.info("Starting integration tests")
        cmd = ["pytest", "--iaas=zure", "--configfile=" + configfile, "integration/"]
        logger.debug("Running command: " + " ".join([v for v in cmd]))
        result = subprocess.run(cmd, capture_output=True, cwd="/gardenlinux/tests")
        logger.info("Integration tests returned with %d" % result.returncode)
        logger.info(result.stdout.decode("utf-8"))
        logger.info(result.stderr.decode("utf-8"))
        if result.returncode == 0:
            return True
        else:
            return False


    def run(self):
        self.upload_image()
        self.upload_ssh_key()

        test_result = self.run_integration_test(self.new_config_file)
        if test_result == True:
            logger.info("Tests successful, deleting image")
            self.delete_image()
            self.delete_ssh_key()
        else:
            logger.info("Tests not successful, instance still running")


class FullTest:
    def __init__(self, args):
        self.config_file = args.config
        self.iaas = args.iaas
        try:
            with open(args.config) as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
        except OSError as e:
            logger.exception(e)
            exit(1)
        self.repo_root = pathlib.Path(__file__).parent.parent
        self.debug = args.debug

    @classmethod
    def init(cls, config):
        return FullTest(config)

    def GetTest(self):
        if self.iaas == "aws":
            return AWSFullTest(self.config["aws"])
        elif self.iaas == "gcp":
            sys.exit("Test for GCP not yet implemented.")
            #return GCPFullTest(self.config["gcp"])
        elif self.iaas == "azure":
            return AzureFullTest(self.config["azure"])
        else:
            sys.exit("Unknown cloud provider.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--iaas", type=str, help="cloud provider")
    parser.add_argument("--config", type=str, help="test configuration")
    parser.add_argument("--debug", action="store_true", help="debug")

    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)

    full = FullTest.init(args)
    test = full.GetTest()
    test.run()


if __name__ == "__main__":
    main()
