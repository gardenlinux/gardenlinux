import dataclasses
import enum
import io
import functools
import typing

import botocore.client
import dacite
import yaml

import glci.model
import paths

GardenlinuxFlavourSet = glci.model.GardenlinuxFlavourSet
GardenlinuxFlavour = glci.model.GardenlinuxFlavour
GardenlinuxFlavourCombination = glci.model.GardenlinuxFlavourCombination
Architecture = glci.model.Architecture

CicdCfg = glci.model.CicdCfg


def cicd_cfg(
    cfg_name: str='default',
    cfg_file=paths.cicd_cfg_path,
) -> CicdCfg:
    with open(cfg_file) as f:
        parsed = yaml.safe_load(f)

    for raw in parsed['cicd_cfgs']:
        cfg = dacite.from_dict(
            data_class=CicdCfg,
            data=raw,
        )
        if cfg.name == cfg_name:
            return cfg
    else:
        raise ValueError(f'not found: {cfg_name=}')


def flavour_sets(
    build_yaml: str=paths.flavour_cfg_path,
) -> typing.List[GardenlinuxFlavourSet]:
    with open(build_yaml) as f:
        parsed = yaml.safe_load(f)

    flavour_sets = [
        dacite.from_dict(
            data_class=GardenlinuxFlavourSet,
            data=flavour_set,
            config=dacite.Config(
                cast=[Architecture, typing.Tuple]
            )
        ) for flavour_set in parsed['flavour_sets']
    ]

    return flavour_sets


def flavour_set(
    flavour_set_name: str,
    build_yaml: str=paths.flavour_cfg_path,
):
    for fs in flavour_sets(build_yaml=build_yaml):
        if fs.name == flavour_set_name:
            return fs
    else:
        raise RuntimeError(f'not found: {flavour_set=}')


def release_manifest(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    key: str,
) -> glci.model.OnlineReleaseManifest:
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

    # patch-in transient attrs
    parsed['s3_key'] = key
    parsed['s3_bucket'] = bucket_name

    manifest = dacite.from_dict(
        data_class=glci.model.OnlineReleaseManifest,
        data=parsed,
        config=dacite.Config(
            cast=[
                glci.model.Architecture,
                typing.Tuple
            ],
        ),
    )

    return manifest


def upload_release_manifest(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    key: str,
    manifest: glci.model.ReleaseManifest,
):
    # workaround: need to convert enums to str
    patch_args = {
        attr: val.value for attr, val in manifest.__dict__.items()
        if isinstance(val, enum.Enum)
    }
    manifest = dataclasses.replace(manifest, **patch_args)

    manifest_bytes = yaml.safe_dump(dataclasses.asdict(manifest)).encode('utf-8')
    manifest_fobj = io.BytesIO(initial_bytes=manifest_bytes)

    return s3_client.upload_fileobj(
        Fileobj=manifest_fobj,
        Bucket=bucket_name,
        Key=key,
        ExtraArgs={
            'ContentType': 'text/yaml',
            'ContentEncoding': 'utf-8',
        },
    )


def enumerate_releases(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    prefix: str=glci.model.ReleaseManifest.manifest_key_prefix,
):
    res = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=prefix,
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


def find_releases(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    flavour_set: glci.model.GardenlinuxFlavourSet,
    build_committish: str,
    gardenlinux_epoch: int,
    prefix: str=glci.model.ReleaseManifest.manifest_key_prefix,
):
    flavours = set(flavour_set.flavours())

    for release in enumerate_releases(
        s3_client=s3_client,
        bucket_name=bucket_name,
        prefix=prefix,
    ):
        if not release.flavour() in flavours:
            continue

        if not release.build_committish == build_committish:
            continue

        if not release.gardenlinux_epoch == gardenlinux_epoch:
            continue

        yield release


@functools.lru_cache
def preconfigured(func: callable, cicd_cfg: glci.model.CicdCfg):
    # depends on `gardener-cicd-base`
    import ccc.aws
    s3_session = ccc.aws.session(cicd_cfg.build.aws_cfg_name)
    s3_client = s3_session.client('s3')

    return functools.partial(
        func,
        s3_client=s3_client,
        bucket_name=cicd_cfg.build.s3_bucket_name,
    )
