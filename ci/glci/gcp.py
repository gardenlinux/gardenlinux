import dataclasses
import tempfile
import time
import logging

import google.cloud.storage.blob
import google.cloud.storage.client
import glci.model
import glci.util


logger = lambda: logging.getLogger(__name__)


def upload_image_to_gcp_store(
    storage_client: google.cloud.storage.Client,
    s3_client,
    release: glci.model.OnlineReleaseManifest,
    build_cfg: glci.model.BuildCfg,
) -> google.cloud.storage.blob.Blob:

    gcp_release_artifact = glci.util.virtual_image_artifact_for_platform('gcp')
    gcp_release_artifact_path = release.path_by_suffix(gcp_release_artifact)
    raw_image_key = gcp_release_artifact_path.s3_key
    s3_bucket_name = gcp_release_artifact_path.s3_bucket_name

    image_blob_name = f'gardenlinux-{release.version}.tar.gz'

    # XXX: rather do streaming
    with tempfile.TemporaryFile() as tfh:
        logger().info(f'downloading image from {build_cfg.s3_bucket_name=}')
        s3_client.download_fileobj(
            Bucket=s3_bucket_name,
            Key=raw_image_key,
            Fileobj=tfh,
        )
        logger().info(f'downloaded image from {build_cfg.s3_bucket_name=}')

        tfh.seek(0)

        logger().info(f're-uploading image to gcp {build_cfg.gcp_bucket_name=} {image_blob_name=}')
        gcp_bucket = storage_client.get_bucket(build_cfg.gcp_bucket_name)
        image_blob = gcp_bucket.blob(image_blob_name)
        image_blob.upload_from_file(
            tfh,
            content_type='application/x-xz',
        )
        logger().info(f'uploaded image {raw_image_key=} to {image_blob_name=}')
        return image_blob


def upload_image_from_gcp_store(
    compute_client,
    image_blob: google.cloud.storage.blob.Blob,
    gcp_project_name: str,
    release: glci.model.OnlineReleaseManifest,
    build_cfg: glci.model.BuildCfg,
) -> glci.model.OnlineReleaseManifest:
    image_name = f'gardenlinux-{release.canonical_release_manifest_key_suffix()}'.replace(
        '.', '-'
    ).replace(
        '_', '-'
    ).strip('-')

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
    op_name = resp['name']

    logger().info(f'waiting for {op_name=}')

    operation = compute_client.globalOperations()
    operation.wait(
        project=gcp_project_name,
        operation=op_name,
    ).execute()

    logger().info(f'import done - removing temporary object from bucket {image_blob.name=}')

    image_blob.delete()

    # make image public
    iam_policies = images.getIamPolicy(
        project=gcp_project_name, resource=image_name
    ).execute()
    if not 'bindings' in iam_policies:
        iam_policies = []
    iam_policies.append({
        'members': ['allAuthenticatedUsers'],
        'role': 'roles/compute.imageUser',
    })

    images.setIamPolicy(
        project=gcp_project_name,
        resource=image_name,
        body={
            'bindings': iam_policies,
        }
    ).execute()

    published_image = glci.model.GcpPublishedImage(
        gcp_image_name=image_name,
        gcp_project_name=gcp_project_name,
    )

    return dataclasses.replace(release, published_image_metadata=published_image)


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

    return upload_image_from_gcp_store(
        compute_client=compute_client,
        image_blob=image_blob,
        gcp_project_name=gcp_project_name,
        release=release,
        build_cfg=build_cfg,
    )
