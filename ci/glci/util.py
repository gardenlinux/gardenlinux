import concurrent.futures
import dataclasses
import enum
import faulthandler
import functools
import io
import logging
import os
import pprint
import typing

import botocore.client
import botocore.exceptions
import dacite
import yaml

import glci.model
import paths

GardenlinuxFlavourSet = glci.model.GardenlinuxFlavourSet
GardenlinuxFlavour = glci.model.GardenlinuxFlavour
GardenlinuxFlavourCombination = glci.model.GardenlinuxFlavourCombination
Architecture = glci.model.Architecture

CicdCfg = glci.model.CicdCfg


def configure_logging():
    faulthandler.enable()
    cfg = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'level': logging.INFO,
                'stream': 'ext://sys.stdout',
            },
        },
        'root': {
            'level': logging.DEBUG,
            'handlers': ['console',],
        },
        'loggers': {
            'googleapiclient.discovery_cache': {
                'level': logging.ERROR,
            },
        },
    }
    logging.config.dictConfig(cfg)


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
            config=dacite.Config(cast=[typing.Tuple]),
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
    absent_ok: bool=False,
) -> glci.model.OnlineReleaseManifest:
    '''
    retrieves and deserialises a gardenlinux release manifest from the specified s3 object
    (expects a YAML or JSON document)
    '''
    buf = io.BytesIO()
    try:
        s3_client.download_fileobj(
            Bucket=bucket_name,
            Key=key,
            Fileobj=buf,
        )
    except botocore.exceptions.ClientError as e:
        if absent_ok and str(e.response['Error']['Code']) == '404':
            return None
        raise e

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


def release_manifest_set(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    manifest_key: str,
    absent_ok: bool=False,
) -> glci.model.OnlineReleaseManifest:
    buf = io.BytesIO()
    try:
        s3_client.download_fileobj(
            Bucket=bucket_name,
            Key=manifest_key,
            Fileobj=buf,
        )
    except botocore.exceptions.ClientError as e:
        if absent_ok and str(e.response['Error']['Code']) == '404':
            return None
        raise e

    buf.seek(0)
    parsed = yaml.safe_load(buf)

    parsed['s3_bucket'] = bucket_name
    parsed['s3_key'] = manifest_key

    print(manifest_key)
    manifest = dacite.from_dict(
        data_class=glci.model.OnlineReleaseManifestSet,
        data=parsed,
        config=dacite.Config(
            cast=[
                glci.model.Architecture,
                typing.Tuple
            ],
        ),
    )
    return manifest


def _json_serialisable_manifest(manifest: glci.model.ReleaseManifest):
    # workaround: need to convert enums to str
    patch_args = {
        attr: val.value for attr, val in manifest.__dict__.items()
        if isinstance(val, enum.Enum)
    }
    manifest = dataclasses.replace(manifest, **patch_args)
    return manifest


def upload_release_manifest(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    key: str,
    manifest: glci.model.ReleaseManifest,
):
    manifest = _json_serialisable_manifest(manifest=manifest)

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


def upload_release_manifest_set(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    key: str,
    manifest_set: glci.model.ReleaseManifestSet,
):
    manifests = [_json_serialisable_manifest(m) for m in manifest_set.manifests]
    manifest_set = dataclasses.replace(manifest_set, manifests=manifests)

    manifest_set_bytes = yaml.safe_dump(dataclasses.asdict(manifest_set)).encode('utf-8')
    manifest_set_fobj = io.BytesIO(initial_bytes=manifest_set_bytes)

    return s3_client.upload_fileobj(
        Fileobj=manifest_set_fobj,
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
) -> typing.Generator[glci.model.ReleaseManifest, None, None]:
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=64)
    _release_manifest = functools.partial(
        release_manifest,
        s3_client=s3_client,
        bucket_name=bucket_name,
    )

    continuation_token = None
    while True:
        ctoken_args = {'ContinuationToken': continuation_token} \
                if continuation_token \
                else {}

        res = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            **ctoken_args,
        )
        if (key_count := res['KeyCount']) == 0:
            return
        is_truncated = bool(res['IsTruncated'])
        continuation_token = res.get('NextContinuationToken')

        print(f'found {key_count} release manifests')

        def wrap_release_manifest(key):
            return _release_manifest(key=key)

        keys = [obj_dict['Key'] for obj_dict in res['Contents']]

        yield from executor.map(wrap_release_manifest, keys)

        if not is_truncated:
            return


def find_release(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    release_identifier: glci.model.ReleaseIdentifier,
    prefix: str=glci.model.ReleaseManifest.manifest_key_prefix,
):
    normalised = glci.model.normalised_release_identifier
    release_manifest_key = release_identifier.canonical_release_manifest_key()

    manifest = release_manifest(
        s3_client=s3_client,
        bucket_name=bucket_name,
        key=release_manifest_key,
        absent_ok=True,
    )

    if not manifest:
        return None

    if (found_ri := normalised(manifest.release_identifier())) \
        == (searched_ri := normalised(release_identifier)):
        return manifest
    else:
        # warn about not matching expected contents from canonical name
        print(f'WARNING: {release_manifest_key=} contained unexpected contents:')
        print('this is the release-identifier we searched for:')
        pprint.pprint(dataclasses.asdict(searched_ri))
        print('this is the release-identifier we found:')
        pprint.pprint(dataclasses.asdict(found_ri))

        return None


def find_releases(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    flavour_set: glci.model.GardenlinuxFlavourSet,
    build_committish: str,
    version: str,
    gardenlinux_epoch: int,
    prefix: str=glci.model.ReleaseManifest.manifest_key_prefix,
):
    flavours = set(flavour_set.flavours())

    for flavour in flavours:
        release_identifier = glci.model.ReleaseIdentifier(
            build_committish=build_committish,
            version=version,
            gardenlinux_epoch=gardenlinux_epoch,
            architecture=flavour.architecture,
            platform=flavour.platform,
            modifiers=flavour.modifiers,
        )

        existing_release = find_release(
            s3_client=s3_client,
            bucket_name=bucket_name,
            release_identifier=release_identifier,
            prefix=prefix,
        )

        if existing_release:
            yield existing_release


def release_set_manifest_name(
    build_committish: str,
    gardenlinux_epoch: int,
    version: str,
    flavourset_name: str,
    build_type: glci.model.BuildType,
):
    BT = glci.model.BuildType

    if build_type in (BT.SNAPSHOT, BT.DAILY):
        return f'{gardenlinux_epoch}-{build_committish[:6]}-{flavourset_name}'
    elif build_type is BT.RELEASE:
        return f'{version}-{flavourset_name}'


def enumerate_release_sets(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    prefix: str=glci.model.ReleaseManifestSet.release_manifest_set_prefix,
) -> typing.Generator[glci.model.ReleaseManifest, None, None]:
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=64)
    _release_manifest_set = functools.partial(
        release_manifest_set,
        s3_client=s3_client,
        bucket_name=bucket_name,
    )

    continuation_token = None
    while True:
        ctoken_args = {'ContinuationToken': continuation_token} \
                if continuation_token \
                else {}

        res = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=prefix,
            **ctoken_args,
        )
        if (key_count := res['KeyCount']) == 0:
            return
        is_truncated = bool(res['IsTruncated'])
        continuation_token = res.get('NextContinuationToken')

        print(f'found {key_count} release manifests')

        keys = [
            key for obj_dict in res['Contents']
            # filter out directories
            if s3_client.head_object(
              Bucket=bucket_name,
              Key=(key := obj_dict['Key']),
            )['ContentType'] != 'application/x-directory'
        ]

        def wrap_release_manifest_set(key):
          return _release_manifest_set(manifest_key=key)

        yield from executor.map(wrap_release_manifest_set, keys)

        if not is_truncated:
            return


def find_release_set(
    s3_client: 'botocore.client.S3',
    bucket_name: str,
    flavourset_name: str,
    build_committish: str,
    gardenlinux_epoch: int,
    version: str,
    build_type: glci.model.BuildType,
    prefix: str=glci.model.ReleaseManifestSet.release_manifest_set_prefix,
    absent_ok=False,
) -> glci.model.ReleaseManifestSet:
    build_type = glci.model.BuildType(build_type)

    manifest_key = os.path.join(
        prefix,
        build_type.value,
        release_set_manifest_name(
            build_committish=build_committish,
            gardenlinux_epoch=gardenlinux_epoch,
            version=version,
            flavourset_name=flavourset_name,
            build_type=build_type,
        ),
    )

    print(manifest_key)

    manifest = release_manifest_set(
        s3_client=s3_client,
        bucket_name=bucket_name,
        manifest_key=manifest_key,
        absent_ok=absent_ok,
    )

    return manifest


@functools.lru_cache
def preconfigured(
    func: callable,
    cicd_cfg: glci.model.CicdCfg=cicd_cfg(),
):
    # depends on `gardener-cicd-base`
    try:
        import ccc.aws
    except ModuleNotFoundError:
        raise RuntimeError('missing dependency: install gardener-cicd-base')

    s3_session = ccc.aws.session(cicd_cfg.build.aws_cfg_name)
    s3_client = s3_session.client('s3')

    return functools.partial(
        func,
        s3_client=s3_client,
        bucket_name=cicd_cfg.build.s3_bucket_name,
    )


class EnumValueYamlDumper(yaml.SafeDumper):
    '''
    a yaml.SafeDumper that will dump enum objects using their values
    '''
    def represent_data(self, data):
        if isinstance(data, enum.Enum):
            return self.represent_data(data.value)
        return super().represent_data(data)
