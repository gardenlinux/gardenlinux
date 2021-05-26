import os

import glci.s3


PACKAGE_BUILD_DIR = 'main'


def upload_packages(
    cicd_cfg_name: str,
    package_path_s3_prefix: str,
    src_dir_path: str = os.getenv('BUILDTARGET', '/workspace/pool'),
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    if not (package_build_cfg := cicd_cfg.package_build):
        raise RuntimeError(f"No package-build config found in cicd-config {cicd_cfg_name}")

    s3_bucket_name = package_build_cfg.s3_bucket_name
    s3_resource = glci.s3.s3_resource_for_aws_cfg_name(package_build_cfg.aws_cfg_name)

    # manipulate paths so that only the 'main' dir is uploaded
    src_dir_path = os.path.join(src_dir_path, PACKAGE_BUILD_DIR)
    package_path_s3_prefix = os.path.join(package_path_s3_prefix, PACKAGE_BUILD_DIR)

    glci.s3.upload_dir(
        s3_resource=s3_resource,
        bucket_name=s3_bucket_name,
        src_dir_path=src_dir_path,
        dest_dir_path=package_path_s3_prefix,
    )
