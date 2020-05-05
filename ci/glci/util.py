import io
import typing

import botocore.client
import dacite
import yaml

import glci.model


def release_manifest(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    key: str,
):
    '''
    retrieves and deserialises a gardenlinux release manifest from the specified s3 object
    (expects a YAML or JSON document)
    '''
    buf = io.BytesIO()
    s3_client.download_fileobj(
        Bucket=bucket_name,
        Key=key,
        Fileobj=buf,
    )
    buf.seek(0)
    parsed = yaml.safe_load(buf)

    manifest = dacite.from_dict(
        data_class=glci.model.ReleaseManifest,
        data=parsed,
        config=dacite.Config(
            cast=[
                glci.model.Architecture,
                typing.Tuple
            ],
        ),
    )

    return manifest


def enumerate_releases(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
):
    res = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=glci.model.ReleaseManifest.manifest_key_prefix,
    )
    if (key_count := res['KeyCount']) == 0:
        return
    print(f'found {key_count} release manifests')

    for obj_dict in res['Contents']:
        key = obj_dict['Key']
        yield release_manifest(
            s3_client=s3_client,
            bucket_name=bucket_name,
            key=key,
        )
