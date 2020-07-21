import dataclasses
import datetime
import hashlib
import io
import json
import lzma
import os
import random
import tarfile
import tempfile
import typing

import glci.model

dc = dataclasses.dataclass

@dc
class OCIConfig:
    pass

@dc
class OCIContainerCfg:
    Hostname: str
    Image: str # sha256-hash
    Domainname: str = ''
    User: str = ''
    AttachStdin: bool = False
    AttachStdout: bool = False
    Tty: bool = False
    OpenStdin: bool = False
    StdinOnce: bool = False
    Env: typing.Tuple[str] = (
        'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
    )
    Cmd: typing.Tuple[str] = ('/bin/sh',)
    ArgsEscaped: bool = False
    Volumes: typing.Optional[typing.Tuple[str]] = None
    WorkingDir: str = ''
    Entrypoint: str = None
    OnBuild: str = None
    Labels: typing.Dict[str, str] = dataclasses.field(
        default_factory=dict,
    )

@dc
class OCI_Fs:
    diff_ids: typing.Tuple[str] # tuple of layer-sha256-digests
    type: str = 'layers'

@dc
class OCIManifestEntry:
    config: OCIContainerCfg
    container_config: OCIContainerCfg
    created: str # iso8601-ts
    container: str # container-hash
    # container_config: OCIContainerCfg
    rootfs: OCI_Fs
    architecture: str='amd64'
    docker_version: str='18.09.7'
    history: typing.Tuple[dict] = ()
    os: str = 'linux'


@dc
class OCIManifest:
    __filename__ = 'manifest.json'
    Config: str # relpath to config.json
    Layers: typing.Tuple[str] # relpaths to <layer>/layer.tar
    RepoTags: typing.Tuple[str] # repo-tags (e.g. eu.gcr.io/foo/bar:latest)


@dc
class LayerContainerCfg:
    Cmd: typing.List[str]


@dc
class LayerCfg:
    container_config: LayerContainerCfg
    created: str # isoformat ts
    id: str # digest


def buf_leng(fileobj):
    leng = fileobj.seek(0, io.SEEK_END)
    fileobj.seek(0)
    return leng


def image_from_rootfs(
    rootfs_tar_xz: str,
    image_reference: str,
):
    '''
    creates an OCI-compliant container image, based on the legacy V1 spec used by docker with exactly one layer, containing
    the filesystem contained in `rootfs_tar_xz`, which is expected to be an xzip-compressed tarfile.

    the resulting file is created as a (named) temporary file, and returned to the caller. The caller is responsible for
    unlinking the file.
    '''
    # extract and calculate sha256 digest
    rootfs_tar = tempfile.NamedTemporaryFile()
    rootfs_sha256_hash = hashlib.sha256()
    with lzma.open(rootfs_tar_xz) as f:
        while chunk := f.read(4069):
            rootfs_sha256_hash.update(chunk)
            rootfs_tar.write(chunk)
    rootfs_sha256_digest = rootfs_sha256_hash.hexdigest()
    rootfs_tar.flush()

    now_ts = datetime.datetime.now().isoformat() + 'Z'
    container_id = hashlib.sha256(f'{random.randint(0, 2 ** 32)}'.encode('utf-8')).hexdigest()
    print(f'{container_id=}')

    # create manifest entry (name it as the hash)
    manifest_entry = OCIManifestEntry(
        created=now_ts,
        container=rootfs_sha256_digest, # deviates from what docker does
        config=OCIContainerCfg(
            Hostname=rootfs_sha256_digest,
            Image=f'sha256:{rootfs_sha256_digest}',
            # use defaults from dataclass definition
        ),
        container_config=OCIContainerCfg(
            Hostname=rootfs_sha256_digest,
            Image=f'sha256:{rootfs_sha256_digest}',
            # use defaults from dataclass definition
        ),
        rootfs=OCI_Fs(
            diff_ids=[f'sha256:{rootfs_sha256_digest}'],
            type='layers',
        ),
        architecture='amd64',
        os='linux',
    )
    manifest_buf = io.BytesIO(json.dumps(dataclasses.asdict(manifest_entry)).encode('utf-8'))
    manifest_buf_leng = buf_leng(manifest_buf)
    manifest_sha256_hash = hashlib.sha256(manifest_buf.read())
    manifest_buf.seek(0)
    manifest_entry_fname = f'{manifest_sha256_hash.hexdigest()}.json'

    image_tar = tarfile.open(tempfile.NamedTemporaryFile().name, 'w')

    manifest_info = tarfile.TarInfo(name=manifest_entry_fname)
    manifest_info.size = manifest_buf_leng
    image_tar.addfile(tarinfo=manifest_info, fileobj=manifest_buf)


    # add img-dir
    img_directory_info = tarfile.TarInfo(name=container_id)
    img_directory_info.type = tarfile.DIRTYPE
    img_directory_info.mode = 0x755
    image_tar.addfile(tarinfo=img_directory_info)


    version_info = tarfile.TarInfo(name=f'{container_id}/VERSION')
    version_buf = io.BytesIO(b'1.0')
    version_buf_leng = buf_leng(version_buf)
    version_info.size = version_buf_leng
    image_tar.addfile(tarinfo=version_info, fileobj=version_buf)

    layer_json_info = tarfile.TarInfo(name=f'{container_id}/json')
    layer_info_buf = io.BytesIO(
        json.dumps(
            dataclasses.asdict(
                LayerCfg(
                    id=container_id,
                    created=now_ts,
                    container_config=LayerContainerCfg(
                        Cmd=[''],
                    ),
                )
            )
        ).encode('utf-8')
    )
    layer_json_info.size = buf_leng(layer_info_buf)
    image_tar.addfile(tarinfo=layer_json_info, fileobj=layer_info_buf)

    layer_tar_fname = f'{container_id}/layer.tar'
    image_tar.add(name=rootfs_tar.name, arcname=layer_tar_fname)

    # add manifest.json
    manifest = OCIManifest(
        Config=manifest_entry_fname,
        Layers=[layer_tar_fname],
        RepoTags=[image_reference],
    )
    manifest_buf = io.BytesIO(
        json.dumps([dataclasses.asdict(manifest)]).encode('utf-8'),
    )
    manifest_info = tarfile.TarInfo(name='manifest.json')
    manifest_info.size = buf_leng(manifest_buf)
    image_tar.addfile(tarinfo=manifest_info, fileobj=manifest_buf)

    # add repositories
    repo, tag = image_reference.split(':')

    repositories_dict = {
        repo: {
            tag: container_id,
        },
    }
    repositories_buf = io.BytesIO(json.dumps(repositories_dict).encode('utf-8'))
    repositories_info = tarfile.TarInfo(name='repositories')
    repositories_info.size = buf_leng(repositories_buf)

    image_tar.addfile(tarinfo=repositories_info, fileobj=repositories_buf)

    image_tar.fileobj.flush()

    print(image_tar.name)
    return image_tar.name


def publish_image(
    release: glci.model.OnlineReleaseManifest,
    publish_cfg: glci.model.OciPublishCfg,
    s3_client,
    publish_oci_image_func: callable,
):
    image_name = f'{publish_cfg.image_prefix}:{release.version}'

    rootfs_key = release.path_by_suffix('rootfs.tar.gz').s3_key
    rootfs_bucket_name = release.path_by_suffix('rootfs.tar.gz').s3_bucket_name

    with tempfile.TemporaryFile() as tfh:
        s3_client.download_fileobj(
            Bucket=rootfs_bucket_name,
            Key=rootfs_key,
            Fileobj=tfh,
        )
        tfh.seek(0)

        oci_image_file = image_from_rootfs(
            rootfs_tar_xz=tfh,
            image_reference=image_name,
        )

    try:
      oci_image_fileobj = open(oci_image_file)

      publish_oci_image_func(
          image_reference=image_name,
          image_file_obj=oci_image_fileobj,
      )
    finally:
      oci_image_fileobj.close()
      os.unlink(oci_image_file)

    published_image_reference = glci.model.OciPublishedImage(
        image_reference=image_name,
    )

    return dataclasses.replace(release, published_image_metadata=published_image_reference)
