import logging
import os
import subprocess
import tempfile

import ccc.aws
import glci.s3

GARDENLINUX_DISTRIBUTION = 'bullseye'

logger = logging.getLogger(__name__)

# TODO: reprepro-config should either be part of the repository or our config-repo.
# Not sure yet what to do with the inital reprepro update


def setup(reprepro_base_dir: str):
    config_dir = os.path.join(reprepro_base_dir, 'conf')
    os.makedirs(config_dir, exist_ok=False)

    with open(os.path.join(config_dir, 'distributions'), 'w') as f:
        f.write(
            'Origin: Gardenlinux-bullseye\n'
            'Label: Gardenlinux-bullseye\n'
            f'Codename: {GARDENLINUX_DISTRIBUTION}\n'
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


def build_package_repository(
    cicd_cfg_name: str,
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name
    session = ccc.aws.session(aws_cfg=aws_cfg_name)
    s3_resource = session.resource('s3')
    s3_bucket_name = cicd_cfg.build.s3_bucket_name

    def _files_with_extension(dir, extension):
        for dirpath, _, filenames in os.walk(os.path.abspath(os.path.realpath(dir))):
            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext and ext == extension:
                    yield os.path.join(dirpath, filename)

    with tempfile.TemporaryDirectory() as reprepro_base_dir:

        setup(reprepro_base_dir=reprepro_base_dir)

        with tempfile.TemporaryDirectory() as tmp_dir:
            # download existing packages from s3 (put there by previous build-steps)
            glci.s3.download_dir_from_s3(
                s3_resource=s3_resource,
                bucket_name=s3_bucket_name,
                s3_dir='packages/',
                local_dir=tmp_dir,
            )
            # add all debian-packages to reprepo-repository
            for file_path in _files_with_extension(tmp_dir, '.deb'):
                logger.info(f"adding '{file_path}' to repository")
                subprocess.run(
                    [
                        'reprepro', '-b', reprepro_base_dir,
                        'includedeb', GARDENLINUX_DISTRIBUTION, file_path,
                    ],
                    capture_output=True,
                    check=True,
                )

        logger.info('uploading to s3-bucket ... ')
        for dir_name in ['pool', 'dists']:
            glci.s3.upload_dir_to_s3(
                s3_resource=s3_resource,
                bucket_name=s3_bucket_name,
                src_dir_path=os.path.join(reprepro_base_dir, dir_name),
                dest_dir_path=dir_name,
            )
