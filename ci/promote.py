#!/usr/bin/env python3

'''
Promotes the specified build results (represented by build result manifests in S3).

An example being the promotion of a build snapshot to a daily build.
'''

import argparse
import concurrent.futures
import enum
import functools
import logging
import logging.config
import os
import sys
import typing

import glci.util

glci.util.configure_logging()

logger = logging.getLogger(__name__)


class BuildType(enum.Enum):
    SNAPSHOT = 'snapshot'
    DAILY = 'daily'
    RELEASE = 'release'


class PromoteMode(enum.Enum):
    MANIFESTS_ONLY = 'manifests_only'
    MANIFESTS_AND_PUBLISH = 'manifests_and_publish'
    RELEASE = 'release'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--flavourset', default='testing')
    parser.add_argument('--committish')
    parser.add_argument('--gardenlinux-epoch', type=int)
    parser.add_argument('--promote-mode', type=PromoteMode)
    parser.add_argument('--version', required=True)
    parser.add_argument('--source', default='snapshots')
    parser.add_argument('--target', type=BuildType, default=BuildType.DAILY)
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--allow-partial', default=False, action='store_true')

    return parser.parse_args()


def publish_image(
    release: glci.model.OnlineReleaseManifest,
    cicd_cfg: glci.model.CicdCfg,
) -> glci.model.OnlineReleaseManifest:
    print(f'running release for {release.platform=}')

    if release.platform == 'ali':
        publish_function = _publish_alicloud_image
    elif release.platform == 'aws':
        publish_function = _publish_aws_image
    elif release.platform == 'gcp':
        publish_function = _publish_gcp_image
    else:
        print(f'do not know how to publish {release.platform=} yet')
        return release

    return publish_function(release, cicd_cfg)


def _publish_alicloud_image(release: glci.model.OnlineReleaseManifest,
                            cicd_cfg: glci.model.CicdCfg,
                            ) -> glci.model.OnlineReleaseManifest:
    import ccc.alicloud
    import glci.model
    import glci.alicloud
    oss_auth = ccc.alicloud.oss_auth('gardenlinux')
    acs_client = ccc.alicloud.acs_client('gardenlinux')
    maker = glci.alicloud.AlicloudImageMaker(
        oss_auth, acs_client, release, cicd_cfg.build)

    import ccc.aws
    s3_client = ccc.aws.session(cicd_cfg.build.aws_cfg_name).client('s3')
    maker.cp_image_from_s3(s3_client)
    return maker.make_image()


def _publish_aws_image(release: glci.model.OnlineReleaseManifest,
                       cicd_cfg: glci.model.CicdCfg,
                       ) -> glci.model.OnlineReleaseManifest:
    import glci.aws
    import ccc.aws
    mk_session = functools.partial(
        ccc.aws.session, aws_cfg=cicd_cfg.build.aws_cfg_name)
    return glci.aws.upload_and_register_gardenlinux_image(
        mk_session=mk_session,
        build_cfg=cicd_cfg.build,
        release=release,
    )


def _publish_gcp_image(release: glci.model.OnlineReleaseManifest,
                       cicd_cfg: glci.model.CicdCfg,
                       ) -> glci.model.OnlineReleaseManifest:
    import glci.gcp
    import ccc.aws
    import ccc.gcp
    import ci.util
    gcp_cfg = ci.util.ctx().cfg_factory().gcp(cicd_cfg.build.gcp_cfg_name)
    storage_client = ccc.gcp.cloud_storage_client(gcp_cfg)
    s3_client = ccc.aws.session(cicd_cfg.build.aws_cfg_name).client('s3')
    compute_client = ccc.gcp.authenticated_build_func(gcp_cfg)('compute', 'v1')
    return glci.gcp.upload_and_publish_image(
        storage_client=storage_client,
        s3_client=s3_client,
        compute_client=compute_client,
        gcp_project_name=gcp_cfg.project(),
        release=release,
        build_cfg=cicd_cfg.build,
    )


def promote(
    releases: typing.Sequence[glci.model.OnlineReleaseManifest],
    target_prefix: str,
    version_str: str,
    promote_mode: PromoteMode,
    cicd_cfg: glci.model.CicdCfg,
    flavour_set: glci.model.GardenlinuxFlavourSet,
):
    upload_release_manifest_set = glci.util.preconfigured(
        func=glci.util.upload_release_manifest_set,
        cicd_cfg=cicd_cfg,
    )

    if promote_mode in (PromoteMode.MANIFESTS_AND_PUBLISH, PromoteMode.RELEASE):
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=len(releases))
        _publish_img = functools.partial(publish_image, cicd_cfg=cicd_cfg)

        print(f'running {len(releases)} publishing jobs in parallel')
        releases = tuple(executor.map(_publish_img, releases))

        for release in releases:
            print(release.published_image_metadata)

    manifest_set = glci.model.ReleaseManifestSet(
        manifests=releases,
        flavour_set_name=flavour_set.name,
    )

    manifest_path = os.path.join(
        target_prefix,
        f'{version_str}-{flavour_set.name}'
    )

    upload_release_manifest_set(
        key=manifest_path,
        manifest_set=manifest_set,
    )

    print(f'uploaded manifest-set: {manifest_path=}')


def main():
    parsed = parse_args()

    cicd_cfg = glci.util.cicd_cfg(cfg_name=parsed.cicd_cfg)
    flavour_set = glci.util.flavour_set(flavour_set_name=parsed.flavourset)
    flavours = set(flavour_set.flavours())
    committish = parsed.committish
    gardenlinux_epoch = parsed.gardenlinux_epoch
    version = parsed.version or f'{gardenlinux_epoch}-{committish[0:6]}'

    find_releases = glci.util.preconfigured(
        func=glci.util.find_releases,
        cicd_cfg=cicd_cfg,
    )

    # XXX hard-code version naming convention
    build_version = f'{gardenlinux_epoch}-{committish[:6]}'

    releases = tuple(find_releases(
        flavour_set=flavour_set,
        version=build_version,
        build_committish=committish,
        gardenlinux_epoch=gardenlinux_epoch,
        prefix=glci.model.ReleaseManifest.manifest_key_prefix,
    )
    )

    is_complete = len(releases) == len(flavours)
    logger.info(f'{flavour_set.name=} contains {len(flavours)} flavours')
    logger.info(f'found {len(releases)} matching release(s) {is_complete=}')

    if not is_complete:
        logger.warning('Release is not complete')
        if not parsed.allow_partial:
            logger.error(f'{parsed.allow_partial=} -> aborting')
            sys.exit(1)

    promote(
        releases=releases,
        target_prefix=os.path.join(
            glci.model.ReleaseManifestSet.release_manifest_set_prefix,
            parsed.target.value,
        ),
        version_str=version,
        promote_mode=parsed.promote_mode,
        cicd_cfg=cicd_cfg,
        flavour_set=flavour_set,
    )


if __name__ == '__main__':
    main()
