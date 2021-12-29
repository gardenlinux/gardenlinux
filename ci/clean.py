import concurrent.futures
import datetime
import itertools
import logging
import os
import typing

import glci.model
import glci.s3
import glci.util

logger = logging.getLogger(__name__)


def clean_release_manifest_sets(
    max_age_days: int=14,
    cicd_cfg: glci.model.CicdCfg=glci.util.cicd_cfg(),
    prefix: str=os.path.join(
      glci.model.ReleaseManifestSet.release_manifest_set_prefix,
      glci.model.PipelineFlavour.SNAPSHOT.value,
    ),
    dry_run: bool=False,
):
    enumerate_release_sets = glci.util.preconfigured(
        glci.util.enumerate_release_sets,
        cicd_cfg=cicd_cfg,
    )

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=64)

    now = datetime.datetime.now()
    oldest_allowed_date = now - datetime.timedelta(days=max_age_days)
    logger.debug(f'{oldest_allowed_date=}')

    s3_client = glci.s3.s3_client(cicd_cfg=cicd_cfg)

    def purge_if_outdated(release_manifest_set: glci.model.ReleaseManifestSet):
        if len(release_manifest_set.manifests) < 1:
            logger.warning(f'{release_manifest_set.s3_key=} did not contain any manifests')
            return (False, release_manifest_set)

        first_manifest = release_manifest_set.manifests[0]
        # all timestamps should usually be pretty close to each other

        if first_manifest.build_ts_as_date() > oldest_allowed_date:
            return (False, release_manifest_set)

        # XXX also purge published images (if any)!
        if dry_run:
            logger.info(
                f'Would delete {release_manifest_set.s3_bucket}/{release_manifest_set.s3_key}'
            )
            return (False, release_manifest_set)
        else:
            s3_client.delete_object(
                Bucket=release_manifest_set.s3_bucket,
                Key=release_manifest_set.s3_key,
            )
            logger.info(f'purged {release_manifest_set.s3_key=}')
            return (True, release_manifest_set)

    for purged, manifest in executor.map(
        purge_if_outdated,
        enumerate_release_sets(prefix=prefix)
    ):
        pass


def clean_single_release_manifests(
    max_age_days: int=14,
    cicd_cfg: glci.model.CicdCfg=glci.util.cicd_cfg(),
    prefix: str=glci.model.ReleaseManifest.manifest_key_prefix,
    dry_run: bool=False,
):
    enumerate_releases = glci.util.preconfigured(
        glci.util.enumerate_releases,
        cicd_cfg=cicd_cfg,
    )

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=64)

    now = datetime.datetime.now()
    oldest_allowed_date = now - datetime.timedelta(days=max_age_days)
    logger.debug(f'{oldest_allowed_date=}')

    s3_client = glci.s3.s3_client(cicd_cfg=cicd_cfg)

    def purge_if_outdated(release_manifest: glci.model.ReleaseManifest):
        if release_manifest.build_ts_as_date() < oldest_allowed_date:
            # XXX also purge published images (if any)!
            if dry_run:
                logger.info(f'would delete {release_manifest.s3_bucket}/{release_manifest.s3_key}')
                return (False, release_manifest)
            else:
                s3_client.delete_object(
                    Bucket=release_manifest.s3_bucket,
                    Key=release_manifest.s3_key,
                )
                logger.info(f'purged {release_manifest.s3_key=}')
                return (True, release_manifest)
        return (False, release_manifest)

    for purged, manifest in executor.map(purge_if_outdated, enumerate_releases()):
        pass


def _enumerate_objects_from_single_release_manifests(
    cicd_cfg: glci.model.CicdCfg=glci.util.cicd_cfg(),
    prefix: str=glci.model.ReleaseManifest.manifest_key_prefix,
) -> typing.Generator[glci.model.S3_ReleaseFile, None, None]:
    enumerate_releases = glci.util.preconfigured(
        glci.util.enumerate_releases,
        cicd_cfg=cicd_cfg,
    )
    for release_manifest in enumerate_releases(prefix=prefix):
        yield from release_manifest.paths


def _enumerate_objects_from_release_manifest_sets(
    cicd_cfg: glci.model.CicdCfg=glci.util.cicd_cfg(),
    prefix: str=glci.model.ReleaseManifestSet.release_manifest_set_prefix,
) -> typing.Generator[glci.model.S3_ReleaseFile, None, None]:
    enumerate_release_sets = glci.util.preconfigured(
        glci.util.enumerate_release_sets,
        cicd_cfg=cicd_cfg,
    )

    for release_manifest_set in enumerate_release_sets(prefix=prefix):
        for release_manifest in release_manifest_set.manifests:
            yield from release_manifest.paths
        if release_manifest_set.logs:
            yield from release_manifest_set.logs


def clean_orphaned_objects(
    cicd_cfg: glci.model.CicdCfg=glci.util.cicd_cfg(),
    prefix='objects',
    dry_run: bool=False,
):
    all_objects = {
        object_descriptor for object_descriptor in
        itertools.chain(
            _enumerate_objects_from_release_manifest_sets(
                cicd_cfg=cicd_cfg,
            ),
            _enumerate_objects_from_single_release_manifests(
                cicd_cfg=cicd_cfg,
            )
        )
    }

    # XXX assume for now that we only use one bucket
    s3_bucket_name = cicd_cfg.build.s3_bucket_name
    all_object_keys = {
        o.s3_key for o in all_objects if o.s3_bucket_name == s3_bucket_name
    }

    logger.debug(f'{len(all_objects)=}')
    logger.debug(f'{len(all_object_keys)=}')

    s3_client = glci.s3.s3_client(cicd_cfg=cicd_cfg)

    continuation_token = None
    while True:
        ctoken_args = {'ContinuationToken': continuation_token} \
                if continuation_token \
                else {}

        res = s3_client.list_objects_v2(
            Bucket=s3_bucket_name,
            Prefix=prefix,
            **ctoken_args,
        )
        if res['KeyCount'] == 0:
            break

        continuation_token = res.get('NextContinuationToken')

        object_keys = {obj_dict['Key'] for obj_dict in res['Contents']}

        # determine those keys that are no longer referenced by any manifest
        loose_object_keys = object_keys - all_object_keys

        if dry_run:
            logger.info(f'would delete {len(loose_object_keys)=} unreferenced objs:')

        else:
            if loose_object_keys:
                s3_client.delete_objects(
                    Bucket=s3_bucket_name,
                    Delete={
                    'Objects': [
                        {'Key': key} for key in loose_object_keys
                    ],
                    },
                )
                logger.info(f'purged {len(loose_object_keys)=} unreferenced objs')

        if not continuation_token:
          break
