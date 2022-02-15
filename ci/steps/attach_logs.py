import datetime
import logging
import os

import glci.model
import glci.s3
import glci.util
import logs

logger = logging.getLogger(__name__)


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

    logger.info(f'upload succeeded: {s3_key}')
    return glci.model.S3_ReleaseFile(
        name=name,
        suffix=name,
        s3_key=s3_key,
        s3_bucket_name=s3_bucket_name,
    )


def _attach_logs_to_single_manifest(
    build_dict: dict[str,str],
    s3_client: glci.s3.s3_client,
    s3_bucket_name: str,
    s3_log_key: str,
):
    for task, key in build_dict.items():
        if key and key.strip():
            logger.info(f'Attach logs from task {task}, {key} to manifest')
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
            manifest_path = (
                f'{glci.model.ReleaseManifest.manifest_key_prefix}/'
                f'{manifest_path_suffix}'
            )
            glci.util.upload_release_manifest(
              s3_client=s3_client,
              bucket_name=s3_bucket_name,
              key=manifest_path,
              manifest=new_manifest,
            )
        else:
            logger.info(f'Task {task} was not built in this run')


def _attach_and_upload_logs(
    architecture: str,
    build_dict: dict[str, str],
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    flavour_set_name: str,
    gardenlinux_epoch: str,
    manifest_set_key: str,
    platform_set: str,
    repo_dir: str,
    version: str,
) -> bool:
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_client = glci.s3.s3_client(cicd_cfg)
    aws_cfg_name = cicd_cfg.build.aws_cfg_name

    log_path = os.path.join(repo_dir, 'build_log_full.zip')
    if not os.path.exists(log_path):
        logger.error("No file found with log files, won't upload.")
        logger.error("Exiting with failure, see logs from previous steps")
        return False

    prefix = datetime.datetime.utcnow().strftime('%Y%m%d-%H%M%S') + '-' + \
        committish[:6] + '-'

    s3_key = 'objects/' + prefix + 'build_log.zip'
    s3_bucket_name = cicd_cfg.build.s3_bucket_name

    logger.info(f'uploaded zipped logs to {s3_key=}')
    uploaded_file = _upload_file(
        log_file_path=log_path,
        s3_key=s3_key,
        s3_client=s3_client,
        s3_bucket_name=s3_bucket_name
    )

    # write a file with the download URL so that it can be later added to the email
    with open(os.path.join(repo_dir, 'log_url.txt'), 'w') as f:
        f.write(
            f'https://{cicd_cfg.build.s3_bucket_name}.s3.{cicd_cfg.build.aws_region}.amazonaws.com/'
            f'{s3_key}'
        )

    # if we create manifests attach logs to all manifests that actually have been build in this run
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)
    if glci.model.BuildTarget.MANIFEST in build_target_set:
        _attach_logs_to_single_manifest(
            build_dict=build_dict,
            s3_client=s3_client,
            s3_bucket_name=s3_bucket_name,
            s3_log_key=s3_key,
        )
    else:
        logger.info(
            f"build target {glci.model.BuildTarget.MANIFEST=} not specified - won't attach logs"
        )
        return True

    logger.info(f'downloading release manifest from s3 {aws_cfg_name=} {s3_bucket_name=}')
    flavour_set = glci.util.flavour_set(flavour_set_name=flavour_set_name)
    if manifest_set_key:
        manifest_set = glci.util.release_manifest_set(
            s3_client=s3_client,
            bucket_name=s3_bucket_name,
            manifest_key=manifest_set_key,
            absent_ok=True,
        )
    else:
        manifest_set = None

    # Manifest-set not found can be caused by:
    # broken build and manifest was never written
    # publish is not in build targets
    # it was a package build
    if manifest_set:
        logger.info('Found existing manifest-set.')
        # Attach log files to manifest-set
        # collect log-keys from single manifests for all artifacts:
        log_files = {uploaded_file, } # note use set as there will be duplicate entries
        platforms = set(platform_set.split(','))
        logger.info(f'Collecting logs from manifests for {platforms=}')

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

                    manifest = glci.util.find_release(
                        release_identifier=release_identifier,
                        s3_client=s3_client,
                        bucket_name=s3_bucket_name,
                    )
                    if manifest:
                        logger.info(f'Found manifest {manifest.s3_key} with logs {manifest.logs}')
                        if manifest.logs:
                            log_files.add(manifest.logs)
                    else:
                        logger.warning(f'Manifest for platform {platform}, \
                            {release_identifier.canonical_release_manifest_key()} not found.')

        logger.info(f'Attaching {len(log_files)} logs to manifest')
        new_manifest_set = manifest_set.with_logfiles(tuple(log_files))

        upload_release_manifest_set = glci.util.preconfigured(
            func=glci.util.upload_release_manifest_set,
            cicd_cfg=cicd_cfg,
        )
        logger.info(f'Uploading manifest set to {manifest_set_key}')
        upload_release_manifest_set(
            key=manifest_set_key,
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
    build_tasks: str,
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    flavour_set_name: str,
    gardenlinux_epoch: str,
    namespace: str,
    pipeline_run_name: str,
    platform_set: str,
    repo_dir: str,
    version: str,
):
    """Logging Concept:
    - collect logs from all pods and containers of this pipeline run and pack into a ZIP file
    - store the ZIP in S3 under objects with a readable key <date>-<time>-<commit>-<kind>_log.zip
    example: 20211201-063143-07f80e-build_log.zip
    If the build is broken and no manifest is created the log zip is standalone and will be cleaned
    up by clean-job together with other outdated artifacts. It can be found by readable key.
    if build is okay attach logs to single manifests for those artifacts being build in this run
    (some may already have been build in earlier runs and thus are already attached to their
    manifests)if this is a publish-build a manifest set is written to S3. Attach logs to this
    manifest set from this run and collect and attach all logs from artifacts that have been built
    in previous runs from their single manifests.
    Append a timestamp to each manifest set so that mutliple and potentially concurrent runs are safe
    Log files are referenced from manifest-sets and thus not cleaned up as long as the manifest-set
    exists. Snapshot manifest sets are cleaned after some time and with that the referenced log
    files.
    Release manifest-sets are never cleaned up and thus the log file are preserved forever.
    Implementation note: We use two result objects: one to indicate in each build if the artifact was
    built or already existed. And the other one to pass the information with the S3 manifest-set key.
    As this is created during publishing and contains the timestamp it can not be recalculated later
    """
    zip_file_path = os.path.join(repo_dir, 'build_log_full.zip')
    logs.load_kube_config()
    pipeline_run = logs.get_pipeline_run(pipeline_run_name, namespace)

    ok = logs.get_and_zip_logs(
        pipeline_run=pipeline_run,
        repo_dir=repo_dir,
        namespace=namespace,
        pipeline_run_name=pipeline_run_name,
        zip_file_path=zip_file_path,
        tail_lines=None,
        only_failed=False,
    )
    if ok:
        tasks = build_tasks.split(',')
        build_dict = {
          task_name: logs.get_task_result(
            task_runs_dict=pipeline_run,
            task_ref_name=task_name,
            result_name='build_result'
          ) for task_name in tasks
        }

        # get the results from previous tasks by directly looking at pipelineRun custom resource:
        manifest_set_key = logs.get_task_result(
            task_runs_dict=pipeline_run,
            task_ref_name='promote-gardenlinux-task',
            result_name='manifest_set_key_result',
        )
        ok = _attach_and_upload_logs(
            architecture=architecture,
            build_dict=build_dict,
            build_targets=build_targets,
            cicd_cfg_name=cicd_cfg_name,
            committish=committish,
            flavour_set_name=flavour_set_name,
            gardenlinux_epoch=gardenlinux_epoch,
            manifest_set_key=manifest_set_key,
            platform_set=platform_set,
            repo_dir=repo_dir,
            version=version,
        )

    # get log excerpts for failed logs to include them in email notification:
    logs.get_failed_excerpts(
        namespace=namespace,
        pipeline_run=pipeline_run,
        pipeline_run_name=pipeline_run_name,
        only_failed=True,
        repo_dir=repo_dir,
        lines=15,
    )

    print(f'Upload logs finished with result {ok}')
    if not ok:
        # write a file with log status (do not exit(1) as we want the task to continue to send
        # notifications)
        with open(os.path.join(repo_dir, 'status.txt'), 'w') as f:
            f.write('Uploading logs to S3 failed')
