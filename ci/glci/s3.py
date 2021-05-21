import os


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
            src_path_relative = os.path.relpath(src_file_path, start=src_dir_path)
            dst_file_path = os.path.join(dest_dir_path, src_path_relative)

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
