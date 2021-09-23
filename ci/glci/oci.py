import collections
import dataclasses
import datetime
import enum
import gziputil
import hashlib
import json
import logging
import lzma
import tempfile
import typing
import zlib

import glci.model
import oci.util as ou


logger = logging.getLogger(__name__)


DOCKER_IMAGE_MANIFEST_V2_S2_MEDIATYPE = 'application/vnd.docker.distribution.manifest.v2+json'
DOCKER_IMAGE_LIST_MEDIATYPE = 'application/vnd.docker.distribution.manifest.list.v2+json'


class OperatingSystem(enum.Enum):
    # For all possible values, see the allowed values of $GOOS
    # https://golang.org/doc/install/source#environment
    LINUX = 'linux'


class Architecture(enum.Enum):
    # For all possible values, see the allowed values of $GOARCH in
    # https://golang.org/doc/install/source#environment
    AMD64 = 'amd64'
    ARM64 = 'arm64'


@dataclasses.dataclass
class ImageManifestV2_2Config:
    size: int
    digest: str
    mediaType: str = 'application/vnd.docker.container.image.v1+json'


@dataclasses.dataclass
class ImageManifestV2_2Layers:
    size: int
    digest: str
    urls: typing.Optional[typing.List[str]] = None
    mediaType: str = 'application/vnd.docker.image.rootfs.diff.tar.gzip'


@dataclasses.dataclass
class ImageManifestV2_2:
    # See https://github.com/distribution/distribution/blob/main/docs/spec/manifest-v2-2.md#image-manifest-field-descriptions
    config: ImageManifestV2_2Config
    layers: typing.List[ImageManifestV2_2Layers]
    schemaVersion: int = 2
    mediaType: typing.Optional[str] = DOCKER_IMAGE_MANIFEST_V2_S2_MEDIATYPE


@dataclasses.dataclass
class PlatformConfig:
    architecture: str
    os: str
    features: typing.List[str] = None
    variant: str = None


@dataclasses.dataclass
class ManifestListEntry:
    digest: str
    platform: PlatformConfig
    size: int
    mediaType: str = DOCKER_IMAGE_MANIFEST_V2_S2_MEDIATYPE


@dataclasses.dataclass
class ManifestList:
    manifests: typing.List[ManifestListEntry]
    mediaType: str = DOCKER_IMAGE_LIST_MEDIATYPE
    schemaVersion: int = 2


@dataclasses.dataclass
class ContainerImageConfig:
    User: typing.Optional[str] = None
    ExposedPorts: typing.Optional[object] = None
    Env: typing.Optional[typing.List[str]] = None
    Entrypoint: typing.Optional[typing.List[str]] = None
    Cmd: typing.Optional[typing.List[str]] = None
    Volumes: typing.Optional[object] = None
    WorkingDir: typing.Optional[str] = None
    Labels: typing.Optional[object] = None
    StopSignal: typing.Optional[str] = None
    Memory: typing.Optional[int] = None
    MemorySwap: typing.Optional[int] = None
    CpuShares: typing.Optional[int] = None
    Healthcheck: typing.Optional[object] = None


@dataclasses.dataclass
class RootfsConfig:
    type: str
    diff_ids: typing.List[str]


@dataclasses.dataclass
class HistoryConfig:
    created: typing.Optional[str] = None
    author: typing.Optional[str] = None
    created_by: typing.Optional[str] = None
    comment: typing.Optional[str] = None
    empty_layer: typing.Optional[bool] = None


@dataclasses.dataclass
class ImageConfig:
    # see https://github.com/moby/moby/blob/v20.10.8/image/spec/v1.2.md#image-json-description
    architecture: str
    author: str
    created: str
    history: typing.List[HistoryConfig]
    os: str
    rootfs: RootfsConfig
    config: typing.Optional[ContainerImageConfig] = None


def publish_container_image_from_tarfile(
    tar_file: typing.Union[str, typing.IO],
    oci_client,
    image_reference: str,
    architecture: Architecture,
    os: OperatingSystem = OperatingSystem.LINUX,
    additional_tags: typing.List[str] = [],
):
    image_reference = ou.normalise_image_reference(image_reference=image_reference)
    image_name = image_reference.rsplit(':', 1)[0]
    image_references = (image_reference,) + tuple([f'{image_name}:{tag}' for tag in additional_tags])

    uncompressed_hash = hashlib.sha256()

    with tempfile.TemporaryFile() as gzip_file:

        compressed_hash = hashlib.sha256()
        length = 0
        src_length = 0
        crc = 0

        with lzma.open(tar_file) as f:
            gzip_file.write(gzip_header := gziputil.gzip_header(fname=b'layer.tar'))
            compressed_hash.update(gzip_header)
            length += len(gzip_header)

            compressor = gziputil.zlib_compressobj()

            while chunk := f.read(1024):
                uncompressed_hash.update(chunk)
                crc = zlib.crc32(chunk, crc)
                src_length += len(chunk)

                chunk = compressor.compress(chunk)
                compressed_hash.update(chunk)
                length += len(chunk)
                gzip_file.write(chunk)

            gzip_file.write((remainder := compressor.flush()))
            compressed_hash.update(remainder)
            length += len(remainder)

            gzip_footer = gziputil.gzip_footer(
                crc32=crc,
                uncompressed_size=src_length,
            )
            gzip_file.write(gzip_footer)
            compressed_hash.update(gzip_footer)
            length += len(gzip_footer)

            gzip_file.seek(0)

            logger.info(f"pushing blob created from tarfile '{tar_file}'")
            oci_client.put_blob(
                image_reference=image_reference,
                digest=(compressed_digest := f'sha256:{compressed_hash.hexdigest()}'),
                octets_count=length,
                data=gzip_file,
            )

    image_config = ImageConfig(
        created=(timestamp :=  datetime.datetime.now().replace(microsecond=0).isoformat() + 'Z'),
        author='Gardenlinux CI',
        architecture=architecture.value,
        os=os.value,
        config=ContainerImageConfig(
            Env=['PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'],
            Cmd=['/bin/sh'],
        ),
        rootfs=RootfsConfig(
            type='layers',
            diff_ids=[f'sha256:{uncompressed_hash.hexdigest()}'],
        ),
        history=[HistoryConfig(created=timestamp)]
    )
    image_config = json.dumps(dataclasses.asdict(image_config)).encode('utf-8')
    image_config_digest = f'sha256:{hashlib.sha256(image_config).hexdigest()}'

    logger.info('pushing blob created from image config')
    oci_client.put_blob(
        image_reference=image_reference,
        digest=image_config_digest,
        octets_count=len(image_config),
        data=image_config,
    )

    image_manifest = ImageManifestV2_2(
        config=ImageManifestV2_2Config(
            digest=image_config_digest,
            size=len(image_config),
        ),
        layers=[
            ImageManifestV2_2Layers(
                digest=compressed_digest,
                size=length,
            ),
        ],
    )
    image_manifest = json.dumps(dataclasses.asdict(image_manifest)).encode('utf-8')
    image_manifest_digest = f'sha256:{hashlib.sha256(image_manifest).hexdigest()}'
    image_manifest_size = len(image_manifest)

    for tgt_ref in image_references:
        logger.info(f'publishing manifest {tgt_ref=}')
        oci_client.put_manifest(
        image_reference=image_reference,
        manifest=image_manifest,
    )

    return image_manifest_digest, image_manifest_size


def _flavour_identifier(
    flavour: glci.model.GardenlinuxFlavour,
    include_arch: bool = True,
) -> str:
    features = [
        f.name.strip('_')
        for f in flavour.calculate_modifiers()
        if f.name != 'oci'
    ]
    if include_arch:
        features = [flavour.architecture] + features

    return '-'.join(features)


def publish_image(
    release: glci.model.OnlineReleaseManifest,
    publish_cfg: glci.model.OciPublishCfg,
    release_build: bool,
    oci_client,
    s3_client,
):
    flavour_identifier = _flavour_identifier(release.flavour())
    image_tag = f'{release.version}-{release.build_committish[:6]}-{flavour_identifier}'
    image_reference = f'{publish_cfg.image_prefix}:{image_tag}'

    additional_image_tags = []
    if release_build:
        additional_image_tags.append(f'{release.version}-{flavour_identifier}')

    publish_from_release(
        release=release,
        image_reference=image_reference,
        oci_client=oci_client,
        s3_client=s3_client,
        additional_tags=additional_image_tags,
    )

    published_image_reference = glci.model.OciPublishedImage(
        image_reference=image_reference,
    )

    return dataclasses.replace(release, published_image_metadata=published_image_reference)


def publish_from_release(
    release: glci.model.OnlineReleaseManifest,
    image_reference: str,
    oci_client,
    s3_client,
    additional_tags=[],
):
    rootfs_key = release.path_by_suffix('rootfs.tar.xz').s3_key
    rootfs_bucket_name = release.path_by_suffix('rootfs.tar.xz').s3_bucket_name

    with tempfile.TemporaryFile() as tfh:
        s3_client.download_fileobj(
            Bucket=rootfs_bucket_name,
            Key=rootfs_key,
            Fileobj=tfh,
        )
        tfh.seek(0)
        logger.info(f'retrieved raw image fs from {rootfs_bucket_name=}')

        image_manifest_digest, image_manifest_size = publish_container_image_from_tarfile(
            tar_file=tfh,
            oci_client=oci_client,
            image_reference=image_reference,
            architecture=Architecture(release.architecture),
            additional_tags=additional_tags,
        )

        logger.info('publishing succeeded')

    return image_manifest_digest, image_manifest_size


def publish_from_release_set(
    release_set: glci.model.OnlineReleaseManifestSet,
    publish_cfg: glci.model.OciPublishCfg,
    oci_client,
    s3_client,
):
    # version is only present in manifests, but should be the same in all
    version = release_set.manifests[0].version
    # we only care about oci-releases
    filtered_manifests = tuple(filter(lambda m: m.platform == 'oci', release_set.manifests))

    # group releases by potential image-tag, ignoring architecture. Releases that end up in the
    # same bucket are just architecture-variants of the same feature-set
    sorted_release_manifests = collections.defaultdict(list)
    for release_manifest in filtered_manifests:
        flavour_identifier = _flavour_identifier(release_manifest.flavour(), include_arch=False)
        image_tag = f'{version}-{flavour_identifier}'
        sorted_release_manifests[image_tag].append(release_manifest)

    logger.info(f'Publishing {len(sorted_release_manifests)} multi-arch images.')

    # create a multiarch-image for each bucket
    for image_tag in sorted_release_manifests:
        image_reference = f'{publish_cfg.image_prefix}:{version}-{image_tag}'
        logger.info(
            f'Publishing multi-arch image {image_reference}. '
            'Beginning to push architecture variants now...'
        )
        image_manifests = []
        for release_manifest in sorted_release_manifests[image_tag]:
            image_manifest_digest, image_manifest_size = publish_from_release(
                release=release_manifest,
                image_reference=image_reference,
                oci_client=oci_client,
                s3_client=s3_client,
            )

            published_image_reference = glci.model.OciPublishedImage(
                image_reference=image_reference,
            )
            dataclasses.replace(release_manifest, published_image_metadata=published_image_reference)

            architecture = Architecture(release_manifest.architecture.value)
            os = OperatingSystem.LINUX  # currently not set in release-sets

            image_manifests.append(
                ManifestListEntry(
                    digest=image_manifest_digest,
                    size=image_manifest_size,
                    platform=PlatformConfig(
                        architecture=architecture.value,
                        os=os.value,
                    )
                )
            )

        logger.info(
            f'Successfully pushed architecture variants for {image_reference}. '
            'Publishing manifest list...'
        )
        manifest_list = ManifestList(manifests=image_manifests)
        oci_client.put_manifest(
            image_reference=image_reference,
            manifest=json.dumps(dataclasses.asdict(
                manifest_list,
                dict_factory=lambda x: {k: v for (k, v) in x if v is not None},
            )).encode('utf-8'),
        )
        logger.info(f'Publishing multi-arch image {image_reference} succeeded')

    return release_set
