#!/usr/bin/env python3

import logging
import os
import subprocess
import tempfile

import ccc.aws

AWS_CONFIG_NAME = 'gardenlinux'
GARDENLINUX_DISTRIBUTION = 'bullseye'
GARDENLINUX_PKGS_BUCKET_NAME = 'gardenlinux-pkgs'
REPREPRO_BASE_DIR = '~/repo/gardenlinux'

logger = logging.getLogger(__name__)

###
### TODO: Move the next few functions to the model
###


def upload_dir_to_s3(
    s3_resource,
    bucket_name: str,
    src_dir_path: str,
    dest_dir_path: str = "/",
):
    bucket = s3_resource.Bucket(name=bucket_name)
    for dirpath, _, filenames in os.walk(src_dir_path):
        for filename in filenames:
            src_file_path = os.path.join(dirpath, filename)
            src_path_relative = os.path.relpath(src_file_path, start=src_dir_path)
            dst_file_path = os.path.join(dest_dir_path, src_path_relative)

            bucket.upload_file(
                Filename=src_file_path,
                Key=dst_file_path,
            )


def download_dir_from_s3(
    s3_resource,
    bucket_name: str,
    s3_dir: str,
    local_dir: str,
):
    bucket = s3_resource.Bucket(name=bucket_name)

    local_dir = os.path.abspath(os.path.realpath(local_dir))

    for s3_obj in bucket.objects.filter(Prefix=s3_dir):

        s3_dirname, s3_filename = os.path.split(s3_obj.key)
        local_dest_dir = os.path.join(local_dir, s3_dirname)
        local_dest_file_path = os.path.join(local_dest_dir, s3_filename)

        os.makedirs(local_dest_dir, exist_ok=True)

        bucket.download_file(Key=s3_obj.key, Filename=local_dest_file_path)


def files_with_extension(
    dir: str,
    extension: str,
):
    for dirpath, _, filenames in os.walk(os.path.abspath(os.path.realpath(dir))):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext and ext == extension:
                yield os.path.join(dirpath, filename)


def create_s3_resource(
    aws_config_name: str,
    region_name: str = None,
):
    session = ccc.aws.session(aws_cfg=aws_config_name, region_name=region_name)
    return session.resource('s3')


# TODO: reprepro-config should either be part of the repository or our config-repo.
# Not sure yet what to do with the inital reprepro update


def setup():
    config_dir = os.path.join(REPREPRO_BASE_DIR, 'conf')
    os.makedirs(config_dir, exist_ok=False)

    with open(os.path.join(config_dir, 'distributions'), 'w') as f:
        f.write(
            'Origin: Gardenlinux-bullseye\n'
            'Label: Gardenlinux-bullseye\n'
            'Codename: bullseye\n'
            'Architectures: amd64\n'
            'Components: gardenlinux\n'
            'Description: Apt repository for Gardenlinux\n'
            'Update: s3-remote\n'
        )

    with open(os.path.join(config_dir, 'updates'), 'w') as f:
        f.write(
            'Name: s3-remote\n'
            'Method: https://gardenlinux-pkgs.s3.eu-central-1.amazonaws.com/\n'
            'Components: gardenlinux\n'
        )

    # subprocess.run(
    #         [
    #             'reprepro', '-b', REPREPRO_BASE_DIR,
    #             'update'
    #         ],
    #         capture_output=True,
    #         check=True,
    #     )


def main():
    s3_resource = create_s3_resource(aws_config_name=AWS_CONFIG_NAME)

    with tempfile.TemporaryDirectory() as tmp_dir:
        # download existing packages from s3 (put there by previous build-steps)
        download_dir_from_s3(
            s3_resource=s3_resource,
            bucket_name=GARDENLINUX_PKGS_BUCKET_NAME,
            s3_dir='packages/',
            local_dir=tmp_dir,
        )
        # add all debian-packages to reprepo-repository
        for file_path in files_with_extension(tmp_dir, '.deb'):
            logger.info(f"adding '{file_path}' to repository")
            subprocess.run(
                [
                    'reprepro', '-b', REPREPRO_BASE_DIR,
                    'includedeb', GARDENLINUX_DISTRIBUTION, file_path,
                ],
                capture_output=True,
                check=True,
            )

    logger.info('uploading to s3-bucket ... ')
    for dir_name in ['pool', 'dists']:
        upload_dir_to_s3(
            s3_resource=s3_resource,
            bucket_name=GARDENLINUX_PKGS_BUCKET_NAME,
            src_dir_path=os.path.join(REPREPRO_BASE_DIR, dir_name),
            dest_dir_path=dir_name,
        )


if __name__ == '__main__':
    setup()
    main()
