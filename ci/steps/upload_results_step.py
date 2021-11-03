import dataclasses
import datetime
import hashlib
import os
import pprint
import sys

import glci.model
import glci.util
import glci.s3
import promote

'''
this script is rendered into build-task from step.py/render_task.py
'''

parsable_to_int = str


def upload_files(
    build_result_fname,
    version_str,
    s3_client,
    s3_bucket_name,
):
    for dirpath, dirs, files in os.walk(build_result_fname):
        for file in files:
            full_path = os.path.join(dirpath, file)
            fname = f'{version_str}-{file}'

            with open(full_path, "rb") as fobj:
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
                suffix=os.path.basename(full_path),
                s3_key=upload_key,
                s3_bucket_name=s3_bucket_name,
            )


def upload_results_step(
    cicd_cfg_name: str,
    committish: str,
    architecture: str,
    platform: str,
    gardenlinux_epoch: parsable_to_int,
    modifiers: str,
    version: str,
    outfile: str,
    build_targets: str,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if not glci.model.BuildTarget.MANIFEST in build_target_set:
        print(f'build target {glci.model.BuildTarget.MANIFEST=} not specified - exiting now')
        sys.exit(0)

    if os.path.isfile('/workspace/skip_build'):
        print('/workspace/skip_build found - skipping upload')
        sys.exit(0)

    build_result_fname = outfile
    if not os.path.isdir(build_result_fname):
        print('ERROR: no build result - see previous step for errs')
        sys.exit(1)

    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_client = glci.s3.s3_client(cicd_cfg)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name
    s3_bucket_name = cicd_cfg.build.s3_bucket_name
    print(f'uploading to s3 {aws_cfg_name=} {s3_bucket_name=}')
    gardenlinux_epoch = int(gardenlinux_epoch)

    # always use <epoch>-<commit-hash> as version
    # -> version denotes the intended, future release version, which is only relevant for marking
    #    a flavourset as actually being released
    upload_version = f'{gardenlinux_epoch}-{committish[:6]}'

    uploaded_relpaths = tuple(upload_files(
        build_result_fname=build_result_fname,
        version_str=upload_version,
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

    # always publish oci image
    if manifest.platform == 'oci':
        release_build = glci.model.BuildTarget.FREEZE_VERSION in build_target_set
        manifest = promote._publish_oci_image(
            release=manifest,
            cicd_cfg=cicd_cfg,
            release_build=release_build,
        )

    manifest_path_suffix = manifest.canonical_release_manifest_key_suffix()
    manifest_path = f'{glci.model.ReleaseManifest.manifest_key_prefix}/{manifest_path_suffix}'

    glci.util.upload_release_manifest(
      s3_client=s3_client,
      bucket_name=s3_bucket_name,
      key=manifest_path,
      manifest=manifest,
    )
    print(f'uploaded manifest: {manifest_path=}\n')
    pprint.pprint(dataclasses.asdict(manifest))
