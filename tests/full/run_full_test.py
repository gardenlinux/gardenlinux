#!/usr/bin/env python3

import tempfile
import logging
import argparse
import os
import pathlib
import sys
from urllib.parse import urlparse
import subprocess
import time

import boto3
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
        try:
            with open(args.config) as f:
                self.config = yaml.load(f, Loader=yaml.FullLoader)
        except OSError as e:
            logger.exception(e)
            exit(1)
        
        self.repo_root = pathlib.Path(__file__).parent.parent.parent
        self.debug = args.debug
        self.aws_config = config['aws']
        self.ec2 = boto3.client('ec2')
        self.s3 = boto3.client('s3')


    @classmethod
    def init(cls, path, debug):
        return FullTest(args)
        try:
            with open(path) as f:
                options = yaml.load(f, Loader=yaml.FullLoader)
        except OSError as e:
            logger.exception(e)
            exit(1)
        
        repo_root = pathlib.Path(__file__).parent.parent.parent
        return FullTest(options, repo_root, debug)


    def upload_ssh_key(self):

        response = self.ec2.describe_key_pairs(KeyNames=[self.aws_config["key_name"]])
        if 'KeyPairs' in response and len(response['KeyPairs']) == 1:
            logger.debug("public key '%s' already uploaded" % self.aws_config["key_name"])
            return
        else:
            self.ec2.import_key_pair(KeyName=config.aws.key_name, PublicKeyMaterial=config.aws.ssh_key)
        
    def delete_ssh_key(self):

        self.ec2.delete_delete_key_pair(KeyName=self.config.aws.key_name)

    def upload_image(self, image_url):
        logger.debug("Uploading image %s" % image_url)
        o = urlparse(image_url)
        if o.scheme != 'file':
            raise NotImplementedError("Only local image file uploads implemented.")
        image_file = o.path
        cmd = [os.path.join(self.repo_root, "bin","make-ec2-ami"), 
            "--bucket", self.aws_config["bucket"],
            "--region", self.aws_config["region"],
            "--image-name", self.aws_config["image_name"],
            "--purpose", "integration-test",
            "--image-overwrite", "false",
            image_file]
        if self.debug:
            cmd = cmd + ["--debug"]
        result = subprocess.run(cmd, capture_output=True)
        if result.returncode != 0:
            sys.exit("Error uploading image %s" % str(result.stderr))
        logger.debug("Result of upload_image %s" % str(result.stdout))
        return json.loads(result.stdout)


    def run_integration_test(self):
        cmd = ["pipenv", "run", "pytest", "--iaas", "aws", "integration/"]
        result = subprocess.run(cmd, capture_output=True, cwd='/gardenlinux/tests')
        print(result)
        if result.returncode == 0:
            return True
        else:
            return False


    def delete_image(self, config):

        # (1) ami
        self.ec2.deregister_image(config['ami-id'])

        # (2) snapshot
        self.ec2.delete_snapshot(config['snapshot-id'])

        # (3) bucket
        if config['image-uploaded'] == True:
            self.s3.delete_object(Bucket='%s',Key='%s' % (self.aws_config['bucket'], self.aws_config['image_name']))


    def run(self):

        self.upload_ssh_key()
        ami_id = self.aws_config['ami_id'] if 'ami_id' in self.aws_config else None
        upload_result = None

        if 'image' in self.aws_config:
            # upload an image and test that
            upload_result = self.upload_image(self.aws_config['image'])
            ami_id = upload_result['ami-id']

        if ami_id == None:
            sys.exit("No image or ami_id specified.")


        self.new_config_file = None
        if upload_result is not None:
            self.new_config_file = "/tmp/test_config_amended.yaml"
            self.aws_config['ami_id'] = upload_result['ami-id']
            # need to provide an updated config
            yaml.dump(self.config)
            with open("/tmp/test_config_amended.yaml", "wb") as f:
                f.write(yaml.dump(self.config))

        if self.new_config_file in not None:
            self.run_integration_test(self.new_config_file)
        else:
            self.run_integration_test(self.config_file)
        delete_image()
        delete_ssh_key()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--provider',
        type=str,
        help="cloud provider"
    )
    parser.add_argument(
        'config',
        type=str,
        help="test configuration"
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help="debug"
    )
    args = parser.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
        handler.setLevel(logging.DEBUG)

    full = FullTest.init(args)
    full.run()

if __name__ == "__main__":
    main()
