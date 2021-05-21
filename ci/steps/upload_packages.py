import os

import glci.s3


def upload_packages(
    cicd_cfg_name: str,
    package_path_s3_prefix: str,
    src_dir_path: str = os.getenv('BUILDTARGET', '/workspace/pool'),
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_bucket_name = cicd_cfg.build.s3_bucket_name
    s3_resource = glci.s3.s3_resource(cicd_cfg)

    glci.s3.upload_dir(
        s3_resource=s3_resource,
        bucket_name=s3_bucket_name,
        src_dir_path=src_dir_path,
        dest_dir_path=package_path_s3_prefix,
    )
