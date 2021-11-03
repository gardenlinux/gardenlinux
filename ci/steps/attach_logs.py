import glci.model
import glci.util
import glci.s3
import logs
import os
import hashlib


def _upload_file(
    log_file_path: str,
    s3_client,
    s3_bucket_name: str,
) -> glci.model.S3_ReleaseFile:
    with open(log_file_path, "rb") as fobj:
        # calculate filehash (use as fname)
        sha1 = hashlib.sha1()
        while (chunk := fobj.read(2048)):
            sha1.update(chunk)
        fobj.seek(0)
        sha1_digest = sha1.hexdigest()
        upload_key = os.path.join('objects', sha1_digest)

        s3_client.upload_fileobj(
          Fileobj=fobj,
          Bucket=s3_bucket_name,
          Key=upload_key,
          ExtraArgs={
              'ContentDisposition': 'attachment; filename="build_log.zip"',
              'ContentType': 'application/zip',
          }
        )

    name, suffix = os.path.splitext(log_file_path)
    print(f'upload succeeded: {upload_key}')
    return glci.model.S3_ReleaseFile(
        name=name,
        suffix=suffix,
        s3_key=upload_key,
        s3_bucket_name=s3_bucket_name,
    )


def _upload_package_file(
    log_file_path: str,
    s3_client,
    s3_bucket_name: str,
    s3_key: str
) -> glci.model.S3_ReleaseFile:
    with open(log_file_path, "rb") as fobj:

        s3_client.upload_fileobj(
          Fileobj=fobj,
          Bucket=s3_bucket_name,
          Key=s3_key,
          ExtraArgs={
              'ContentDisposition': 'attachment; filename="build_log.zip"',
              'ContentType': 'application/zip',
          }
        )

    name, suffix = os.path.splitext(log_file_path)
    print(f'upload succeeded: {s3_key}')
    return glci.model.S3_ReleaseFile(
        name=name,
        suffix=suffix,
        s3_key=s3_key,
        s3_bucket_name=s3_bucket_name,
    )


def _attach_and_upload_logs(
    architecture: str,
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    gardenlinux_epoch: str,
    modifiers: str,
    platform: str,
    repo_dir: str,
    version: str,
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_client = glci.s3.s3_client(cicd_cfg)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name
    s3_bucket_name = cicd_cfg.build.s3_bucket_name
    s3_package_bucket_name = cicd_cfg.package_build.s3_bucket_name

    log_path = os.path.join(repo_dir, 'build_log_full.zip')
    if not os.path.exists(log_path):
        print("No file found with log files, won't upload.")
        print("Exiting with failure, see logs from previous steps")
        return False

    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)
    if not glci.model.BuildTarget.MANIFEST in build_target_set:
        print(f'build target {glci.model.BuildTarget.MANIFEST=} not specified - skip upload')
        return True

    manifest_available = True
    if not platform.strip() or not modifiers.strip():
        print('No platform or modifiers given, cannot find release manifest, log upload skipped.')
        print('This is probably a package build.')
        manifest_available = False

    if manifest_available:
        print(f'downloading release manifest from s3 {aws_cfg_name=} {s3_bucket_name=}')
        find_release = glci.util.preconfigured(
            func=glci.util.find_release,
            cicd_cfg=glci.util.cicd_cfg(cicd_cfg_name)
        )

        modifiers = tuple(modifiers.split(','))
        manifest = find_release(
            release_identifier=glci.model.ReleaseIdentifier(
                build_committish=committish,
                version=version,
                gardenlinux_epoch=int(gardenlinux_epoch),
                architecture=glci.model.Architecture(architecture),
                platform=platform,
                modifiers=modifiers,
            ),
            s3_client=s3_client,
            bucket_name=s3_bucket_name,
        )

        if not manifest:
            print('Could not find release-manifest, attaching logs to manifest failed.')
            return False

        # upload file:
        upload_file_gen = _upload_file(
            log_file_path=log_path,
            s3_client=s3_client,
            s3_bucket_name=s3_bucket_name
        )

        # upload log and attach to manifest
        # copy manifest and attach test_results
        s3_key = upload_file_gen.s3_key
        print(f'uploaded zipped logs to {s3_key=}')
        new_manifest = manifest.with_logfile(s3_key)

        # upload manifest
        manifest_path_suffix = manifest.canonical_release_manifest_key_suffix()
        manifest_path = f'{glci.model.ReleaseManifest.manifest_key_prefix}/{manifest_path_suffix}'
        glci.util.upload_release_manifest(
          s3_client=s3_client,
          bucket_name=s3_bucket_name,
          key=manifest_path,
          manifest=new_manifest,
        )
    else:
        upload_file_gen = _upload_package_file(
            log_file_path=log_path,
            s3_client=s3_client,
            s3_bucket_name=s3_package_bucket_name,
            s3_key='last_package_build_log.zip',
        )
        s3_key = upload_file_gen.s3_key
        print(f'uploaded zipped logs to {s3_key=}')

    # write a file with the download URL so that it can be later added to the email
    with open(os.path.join(repo_dir, 'log_url.txt'), 'w') as f:
        f.write(f'https://gardenlinux.s3.eu-central-1.amazonaws.com/{s3_key}')


def upload_logs(
    architecture: str,
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    gardenlinux_epoch: str,
    modifiers: str,
    namespace: str,
    pipeline_run_name: str,
    platform: str,
    repo_dir: str,
    version: str,
):
    zip_file_path = os.path.join(repo_dir, 'build_log_full.zip')
    ok = logs.get_and_zip_logs(
        repo_dir=repo_dir,
        namespace=namespace,
        pipeline_run_name=pipeline_run_name,
        zip_file_path=zip_file_path,
        tail_lines=None,
        only_failed=False,
    )
    if ok:
        _attach_and_upload_logs(
            architecture=architecture,
            build_targets=build_targets,
            cicd_cfg_name=cicd_cfg_name,
            committish=committish,
            gardenlinux_epoch=gardenlinux_epoch,
            modifiers=modifiers,
            platform=platform,
            repo_dir=repo_dir,
            version=version,
        )
