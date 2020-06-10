import dataclasses
import datetime
import hashlib
import io
import os
import sys
import tarfile

import yaml

import ccc.aws # dependency towards github.com/gardener/cc-utils

import glci.model
import glci.util

'''
this script is rendered into build-task from step.py/render_task.py
'''

parsable_to_int = str


def upload_fname(suffix: str):
  return f'{fname_prefix}-{version_str}-{suffix}'


def upload_files(
    build_result_fname,
    s3_client,
    s3_bucket_name,
):
  with tarfile.open(build_result_fname) as tf:
    for tarinfo in tf:
      if not tarinfo.isfile():
        continue
      tar_fname = tarinfo.name.lstrip('./')
      fname = upload_fname(suffix=tar_fname)
      fobj = tf.extractfile(tarinfo)

      # calculate filehash (use as fname)
      sha1 = hashlib.sha1()
      while (chunk := fobj.read(2048)):
        sha1.update(chunk)
      fobj.seek(0)
      sha1_digest = sha1.hexdigest()
      upload_key = os.path.join('objects', sha1_digest)

      # XXX todo: add content-type
      s3_client.upload_fileobj(
        Fileobj=fobj,
        Bucket=s3_bucket_name,
        Key=upload_key,
      )
      print(f'upload succeeded: {upload_key}')
      yield glci.model.S3_ReleaseFile(
        name=fname,
        suffix=tar_fname,
        s3_key=upload_key,
        s3_bucket_name=s3_bucket_name,
      )


def upload_results_step(
    cicd_cfg_name: str,
    committish: str,
    architecture: str,
    platform: str,
    gardenlinux_epoch: parsable_to_int,
    fnameprefix: str,
    modifiers: str,
    version: str,
    outfile: str,
):
    if os.path.isfile('/workspace/skip_build'):
      print('/workspace/skip_build found - skipping upload')
      sys.exit(0)

    if not os.path.isfile(build_result_fname):
      print('ERROR: no build result - see previous step for errs')
      sys.exit(1)

    build_result_fname = outfile
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name
    s3_bucket_name = cicd_cfg.build.s3_bucket_name
    session = ccc.aws.session(aws_cfg_name)
    s3_client = session.client('s3')
    print(f'uploading to s3 {aws_cfg_name=} {s3_bucket_name=}')
    gardenlinux_epoch = int(gardenlinux_epoch)
    short_committish = committish[:6]
    version_str = version
    fname_prefix = fnameprefix

    uploaded_relpaths = tuple(upload_files(
        build_result_fname=build_result_fname,
        s3_client=s3_client,
        s3_bucket_name=s3_bucket_name,
    ))

    modifiers = [
      modifier_str for modifier_str
      in modifiers.split(',') if modifier_str
    ]

    # add manifest (to be able to identify all relevant artifacts later)
    manifest = glci.model.ReleaseManifest(
      build_committish=committish,
      version=version,
      build_timestamp=datetime.datetime.now().isoformat(),
      gardenlinux_epoch=gardenlinux_epoch,
      architecture=glci.model.Architecture(architecture).value,
      platform=platform,
      modifiers=modifiers,
      paths=uploaded_relpaths,
      published_image_metadata=None,
    )

    manifest_path_suffix = manifest.canonical_release_manifest_key_suffix()
    manifest_path = f'{glci.model.ReleaseManifest.manifest_key_prefix}/{manifest_path_suffix}'

    glci.util.upload_release_manifest(
      s3_client=s3_client,
      bucket_name=s3_bucket_name,
      key=manifest_path,
      manifest=manifest,
    )
    print(f'uploaded manifest: {manifest_path=}')
