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


def _attach_logs_to_single_manifest(
    build_dict_str: str,
    s3_client: glci.s3.s3_client,
    s3_bucket_name: str,
    s3_log_key: str,
):
    build_dict = json.loads(build_dict_str)
    for task, key in build_dict.items():
        if key and key.strip():
            print(f'Attach logs from task {task}, {key} to manifest')
            manifest = glci.util.release_manifest(
                s3_client=s3_client,
                bucket_name=s3_bucket_name,
                key=key,
            )
            name = os.path.basename(s3_log_key)
            log_entry = glci.model.S3_ReleaseFile(
                name=name,
                suffix=name,
                s3_key=s3_log_key,
                s3_bucket_name=s3_bucket_name,
            )
            new_manifest = manifest.with_logfile(log_entry)
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
            print(f'Task {task} was not built in this run')


def _attach_and_upload_logs(
    architecture: str,
    build_dict_str: str,
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    flavour_set: str,
    gardenlinux_epoch: str,
    is_package_build: bool,
    platform_set: str,
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

    if is_package_build:
        return True

    # if we create manifests attach logs to all manifests that actually have been build in this run
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)
    if glci.model.BuildTarget.MANIFEST in build_target_set:
        _attach_logs_to_single_manifest(
            build_dict_str=build_dict_str,
            s3_client=s3_client,
            s3_bucket_name=s3_bucket_name,
            s3_log_key=s3_key,
        )
    else:
        print(f'build target {glci.model.BuildTarget.MANIFEST=} not specified - do not attach logs')
        return True

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

    # Manifest-set not found can be caused by:
    # broken build and manifest was never written
    # publish is not in build targets
    # it was a package build
    if manifest_set:
        print('Found existing manifest-set.')
        # Attach log files to manifest-set
        # collect log-keys from single manifests for all artifacts:
        log_files = {uploaded_file, } # note use set as there will be duplicate entries
        platforms = set(platform_set.split(','))
        print(f'Collecting logs from manifests for {platforms=}')

        for platform in platforms:
            for flavour in flavour_set.flavours():
                if flavour.platform == platform:
                    modifiers = sorted((m.name for m in flavour.calculate_modifiers()))
                    release_identifier = glci.model.ReleaseIdentifier(
                            build_committish=committish,
                            version=version,
                            gardenlinux_epoch=int(gardenlinux_epoch),
                            architecture=glci.model.Architecture(architecture),
                            platform=platform,
                            modifiers=modifiers,
                        )

                    print(f'Created release identifier for {release_identifier=}')
                    manifest = glci.util.find_release(
                        release_identifier=release_identifier,
                        s3_client=s3_client,
                        bucket_name=s3_bucket_name,
                    )
                    if manifest:
                        print(f'Found manifest {manifest.s3_key} with logs {manifest.logs}')
                        if manifest.logs:
                            log_files.add(manifest.logs)
                    else:
                        print(f'Manifest for platform {platform}, \
                            {release_identifier.canonical_release_manifest_key()} not found.')

        print(f'Attaching {len(log_files)} logs to manifest')
        new_manifest_set = manifest_set.with_logfiles(tuple(log_files))

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
        print(f'Uploading manifest set to {manifest_path}')
        upload_release_manifest_set(
            key=manifest_path,
            manifest_set=new_manifest_set,
        )

    # if we are in a Release build logs mut be always attached and a missing manifest is a
    # hard error
    elif glci.model.BuildType.RELEASE in build_target_set:
        print('Could not find release-manifest-set in release build, exit with failure')
        return False

    return True


def upload_logs(
    architecture: str,
    build_dict_str: str,
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    flavourset: str,
    gardenlinux_epoch: str,
    namespace: str,
    pipeline_run_name: str,
    platform_set: str,
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
            architecture=architecture,
            build_dict_str=build_dict_str,
            build_targets=build_targets,
            cicd_cfg_name=cicd_cfg_name,
            committish=committish,
            flavour_set=flavourset,
            gardenlinux_epoch=gardenlinux_epoch,
            is_package_build='gl-packages' in pipeline_run_name,
            platform_set=platform_set,
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
