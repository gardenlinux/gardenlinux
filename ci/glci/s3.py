import os
import glci.model
import glci.util


def _s3_session(aws_cfg_name: str):
    try:
        import ccc.aws
    except ModuleNotFoundError:
        raise RuntimeError('missing dependency: install gardener-cicd-base')

    return ccc.aws.session(aws_cfg_name)


def s3_client_for_aws_cfg_name(aws_cfg_name: str):
    return _s3_session(aws_cfg_name).client('s3')


def s3_resource_for_aws_cfg_name(aws_cfg_name: str):
    return _s3_session(aws_cfg_name).resource('s3')


def s3_client(cicd_cfg: glci.model.CicdCfg):
    return s3_client_for_aws_cfg_name(cicd_cfg.build.aws_cfg_name)


def s3_resource(cicd_cfg: glci.model.CicdCfg):
    return s3_resource_for_aws_cfg_name(cicd_cfg.build.aws_cfg_name)


def upload_dir(
    s3_resource,
    bucket_name: str,
    src_dir_path: str,
    dest_dir_path: str = "/",
):
    bucket = s3_resource.Bucket(name=bucket_name)
    for dirpath, _, filenames in os.walk(src_dir_path):
        for filename in filenames:
            src_file_path = os.path.join(dirpath, filename)

            # clean-up filename
            processed_filename = filename.replace('+', '')

            relative_file_path = os.path.relpath(
                os.path.join(dirpath, processed_filename),
                start=src_dir_path,
            )

            dst_file_path = os.path.join(dest_dir_path, relative_file_path)

            if os.path.exists(src_file_path) and os.path.isfile(src_file_path):
                bucket.upload_file(
                    Filename=src_file_path,
                    Key=dst_file_path,
                )


def download_dir(
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
