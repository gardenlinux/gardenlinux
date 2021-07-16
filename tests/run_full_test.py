#!/usr/bin/env python3

import tempfile
import logging
import argparse
import os
import pathlib
import sys
from urllib.parse import urlparse
import subprocess
import selectors
import time
import paramiko

import boto3
import botocore
import yaml
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


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
        self.aws_config = self.config["aws"]
        self.ec2 = boto3.client("ec2")
        self.s3 = boto3.client("s3")

        # dir_path = os.path.dirname(os.path.realpath(__file__))
        # self.gardenlinux_bin = os.path.join(dir_path, os.pardir, "bin")

    @classmethod
    def init(cls, args):
        return FullTest(args)

    def aws_upload_ssh_key(self):
        response = self.ec2.describe_key_pairs()
        if "KeyPairs" in response:
            for kp in response["KeyPairs"]:
                if kp["KeyName"] == self.aws_config["key_name"]:
                    logger.debug(
                        "public key '%s' already uploaded" % self.aws_config["key_name"]
                    )
                    return

        logger.debug("Uploading public key '%s' " % self.aws_config["key_name"])
        k = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa_gardenlinux_test")
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

    def aws_upload_image(self, image_url):
        o = urlparse(image_url)
        if o.scheme != "" and o.scheme != "file":
            raise NotImplementedError("Only local image file uploads implemented.")
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

    def aws_run_integration_test(self, configfile):
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

    def run_aws_integration_test(self):

        self.aws_upload_ssh_key()
        ami_id = self.aws_config["ami_id"] if "ami_id" in self.aws_config else None
        upload_result = None

        if "image" in self.aws_config:
            # upload an image and test that
            logger.info(
                "Uploading new image %s to AWS for test" % self.aws_config["image"]
            )
            upload_result = self.aws_upload_image(self.aws_config["image"])
            ami_id = upload_result["ami-id"]

        if ami_id == None:
            logger.error("No imge or ami_id specifified")
            os.exit(1)

        self.new_config_file = "/tmp/test_config_amended.yaml"
        if upload_result is not None:
            self.aws_config["ami_id"] = upload_result["ami-id"]
        with open("/tmp/test_config_amended.yaml", "w") as f:
            yaml.dump(self.config, f)

        test_result = self.aws_run_integration_test(self.new_config_file)
        if test_result == True:
            logger.info("Tests successful, deleting image")
            self.delete_image()
            self.delete_ssh_key()
        else:
            logger.info("Tests not successful, instance still running")

    def run(self):

        if self.iaas == "aws":
            self.run_aws_integration_test()
        elif self.iaas == "gcp":
            logger.error("Test for GCP no yet implemented.")
            os.exit(1)
        elif self.iaas == "azure":
            logger.error("Test for Azure not yet implemented.")
            os.exit(1)
        else:
            logger.error("Unknown cloud provider.")
            os.exit(1)


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
    full.run()


if __name__ == "__main__":
    main()
