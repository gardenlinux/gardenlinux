import datetime
import json
import os

import glci.model
import glci.util
import glci.s3
import logs


def _upload_file(
    log_file_path: str,
    s3_key: str,
    s3_client,
    s3_bucket_name: str,
) -> glci.model.S3_ReleaseFile:
    print(f'Uploading logs to {s3_key}')
    name = os.path.basename(s3_key)
    with open(log_file_path, "rb") as fobj:
        s3_client.upload_fileobj(
            Fileobj=fobj,
            Bucket=s3_bucket_name,
            Key=s3_key,
            ExtraArgs={
                'ContentDisposition': f'attachment; filename="{name}"',
                'ContentType': 'application/zip',
            }
        )

    print(f'upload succeeded: {s3_key}')
    return glci.model.S3_ReleaseFile(
        name=name,
        suffix=name,
        s3_key=s3_key,
        s3_bucket_name=s3_bucket_name,
    )


def _attach_and_upload_logs(
    build_dict_str: str,
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    flavour_set: str,
    gardenlinux_epoch: str,
    is_package_build: bool,
    promote_target: str,
    repo_dir: str,
    version: str,
) -> bool:
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_client = glci.s3.s3_client(cicd_cfg)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name

    log_path = os.path.join(repo_dir, 'build_log_full.zip')
    if not os.path.exists(log_path):
        print("No file found with log files, won't upload.")
        print("Exiting with failure, see logs from previous steps")
        return False

    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)
    if not glci.model.BuildTarget.MANIFEST in build_target_set:
        print(f'build target {glci.model.BuildTarget.MANIFEST=} not specified - skip upload')
        return True

    prefix = 'objects/' + datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S') + '-' + \
        committish[:6] + '-'

    if is_package_build:
        s3_key = prefix + 'package_build_log.zip',
        s3_bucket_name = cicd_cfg.package_build.s3_bucket_name
    else:
        s3_key = prefix + 'build_log.zip'
        s3_bucket_name = cicd_cfg.build.s3_bucket_name

    print(f'uploaded zipped logs to {s3_key=}')
    uploaded_file = _upload_file(
        log_file_path=log_path,
        s3_key=s3_key,
        s3_client=s3_client,
        s3_bucket_name=s3_bucket_name
    )

    # write a file with the download URL so that it can be later added to the email
    with open(os.path.join(repo_dir, 'log_url.txt'), 'w') as f:
        f.write(f'https://gardenlinux.s3.eu-central-1.amazonaws.com/{s3_key}')

    build_dict = json.loads(build_dict_str)
    for task, key in build_dict.items():
        if key and key.strip():
            print(f'Task {task} build result uploaded to: {key}')
        else:
            print(f'Task {task} was not built in this run')

    if not is_package_build:
        print(f'downloading release manifest from s3 {aws_cfg_name=} {s3_bucket_name=}')
        build_type = glci.model.BuildType(promote_target)
        flavour_set = glci.util.flavour_set(flavour_set_name=flavour_set)
        manifest_set = glci.util.find_release_set(
            s3_client=s3_client,
            bucket_name=s3_bucket_name,
            flavourset_name=flavour_set.name,
            build_committish=committish,
            gardenlinux_epoch=int(gardenlinux_epoch),
            version=version,
            build_type=build_type,
            absent_ok=True,
        )
        print(f'Found existing manifest-set.')

        # Manifest-set not found can be caused by:
        # broken build and manifest was never written
        # publish is not in build targets
        # it was a package build
        if manifest_set:
            # Attach log files to manifest-set
            print(f'old logs: {manifest_set.logs}')
            new_manifest_set = manifest_set.with_logfile(uploaded_file)
            print(f' - log-key: {new_manifest_set.logs}')

            manifest_path = os.path.join(
                glci.model.ReleaseManifestSet.release_manifest_set_prefix,
                build_type.value,
                glci.util.release_set_manifest_name(
                    build_committish=committish,
                    gardenlinux_epoch=gardenlinux_epoch,
                    version=version,
                    flavourset_name=flavour_set.name,
                    build_type=build_type,
                    with_timestamp=True,
                ),
            )

            upload_release_manifest_set = glci.util.preconfigured(
                func=glci.util.upload_release_manifest_set,
                cicd_cfg=cicd_cfg,
            )
            upload_release_manifest_set(
                key=manifest_path,
                manifest_set=new_manifest_set,
            )
        else:
            print('Could not find release-manifest-set')

    # if we are in a Release build logs mut be always attached and a missing manifest is a
    # hard error
    if not manifest_set and glci.model.BuildType.RELEASE in build_target_set:
        print('Could not find release-manifest-set in release build, exit with failure')
        return False
    else:
        return True


def upload_logs(
    build_dict_str: str,
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    flavourset: str,
    gardenlinux_epoch: str,
    namespace: str,
    pipeline_run_name: str,
    promote_target: str,
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
        ok = _attach_and_upload_logs(
            build_dict_str=build_dict_str,
            build_targets=build_targets,
            cicd_cfg_name=cicd_cfg_name,
            committish=committish,
            flavour_set=flavourset,
            gardenlinux_epoch=gardenlinux_epoch,
            is_package_build = 'gl-packages' in pipeline_run_name,
            promote_target=promote_target,
            repo_dir=repo_dir,
            version=version,
        )

    print(f'Upload logs finished with result {ok}')
    if not ok:
        # write a file with log status (do not exit(1) as we want the task to continue to send
        # notifications)
        with open(os.path.join(repo_dir, 'status.txt'), 'w') as f:
            f.write('Uploading logs to S3 failed')
