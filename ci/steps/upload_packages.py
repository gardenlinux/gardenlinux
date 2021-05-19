import os

import ccc.aws
import glci.s3

AWS_CONFIG_NAME = 'gardenlinux'
GARDENLINUX_PKGS_BUCKET_NAME = 'gardenlinux-pkgs'


def main():
    session = ccc.aws.session(aws_cfg=AWS_CONFIG_NAME)
    s3_resource = session.resource('s3')

    dir_to_upload = os.path.join(os.getenv('BUILDTARGET', '/workspace/pool'), 'main')

    glci.s3.upload_dir(
        s3_resource=s3_resource,
        bucket_name=GARDENLINUX_PKGS_BUCKET_NAME,
        src_dir_path=dir_to_upload,
        dest_dir_path='packages'
    )


if __name__ == '__main__':
    main()
