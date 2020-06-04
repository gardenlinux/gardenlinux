import tempfile
import time
import logging

import google.cloud.storage.blob
import google.cloud.storage.client
import glci.model


logger = lambda: logging.getLogger(__name__)


def upload_image_to_gcp_store(
    storage_client: google.cloud.storage.Client,
    s3_client,
    release: glci.model.OnlineReleaseManifest,
    build_cfg: glci.model.BuildCfg,
) -> google.cloud.storage.blob.Blob:
    image_blob_name = f'gardenlinux-{release.version}'
    raw_image_key = release.path_by_suffix('rootfs.tar.xz').rel_path

    # XXX: rather do streaming
    with tempfile.TemporaryFile() as tfh:
        logger().info(f'downloading image from {build_cfg.s3_bucket_name=}')
        s3_client.download_fileobj(
            Bucket=build_cfg.s3_bucket_name,
            Key=raw_image_key,
            Fileobj=tfh,
        )
        logger().info(f'downloaded image from {build_cfg.s3_bucket_name=}')
        tfh.seek(0)
        gcp_bucket = storage_client.get_bucket(build_cfg.gcp_bucket_name)
        image_blob = gcp_bucket.blob(image_blob_name)
        image_blob.upload_from_file(tfh)
        logger().info(f'uploaded image {raw_image_key=} to {image_blob_name=}')
        return image_blob


def upload_image_from_gcp_store(
    compute_client,
    image_blob: google.cloud.storage.blob.Blob,
    gcp_project_name: str,
    release: glci.model.OnlineReleaseManifest,
    build_cfg: glci.model.BuildCfg,
):
    image_name = f'gardenlinux-{release.version}'

    images = compute_client.images()

    insertion_rq = images.insert(
        project=gcp_project_name,
        body={
            'description': 'gardenlinux',
            'name': image_name,
            'rawDisk': {
                'source': image_blob.generate_signed_url(int(time.time())),
            },
        },
    )

    resp = insertion_rq.execute()

    print(resp)


def upload_and_publish_image(
    storage_client: google.cloud.storage.Client,
    s3_client,
    compute_client,
    gcp_project_name: str,
    release: glci.model.OnlineReleaseManifest,
    build_cfg: glci.model.BuildCfg,
):
    image_blob = upload_image_to_gcp_store(
        storage_client=storage_client,
        s3_client=s3_client,
        release=release,
        build_cfg=build_cfg,
    )

    upload_image_from_gcp_store(
        compute_client=compute_client,
        image_blob=image_blob,
        gcp_project_name=gcp_project_name,
        release=release,
        build_cfg=build_cfg,
    )

    # XXX todo: patch upload metadata into returned `release`
    return release
