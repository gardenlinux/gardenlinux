#!/usr/bin/env python3

import logging
import argparse
import os
import sys

import boto3
import yaml

logger = logging.getLogger(__name__)

root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root.addHandler(handler)

class FullTest:

    def __init__(self, config):
        self.config = config

    @classmethod
    def init(path):
        try:
            with open(path) as f:
                options = yaml.load(f, Loader=yaml.FullLoader)
        except OSError as e:
            logger.exception(e)
            exit(1)
        return FullTest(options)

def upload_ssh_key():
    pass

def upload_image():
    pass

def run_integration_test():
    pass

def delete_image():
    pass

def delete_ssh_key():
    pass

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
    args = parser.parse_args()
    config = load_config(args.config)

    upload_ssh_key()
    upload_image()
    run_integration_test()
    delete_image()
    delete_ssh_key()

if __name__ == "__main__":
    main()

