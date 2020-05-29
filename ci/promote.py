#!/usr/bin/env python3

'''
Promotes the specified build results (represented by build result manifests in S3).

An example being the promotion of a build snapshot to a daily build.
'''

import argparse
import enum
import logging
import logging.config
import os
import sys
import typing

import glci.util

cfg = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': logging.INFO,
            'stream': 'ext://sys.stdout',
        },
    },
    'root': {
        'level': logging.DEBUG,
        'handlers': ['console',],
    },
}
logging.config.dictConfig(cfg)
logger = logging.getLogger(__name__)


class BuildType(enum.Enum):
    SNAPSHOT = 'snapshot'
    DAILY = 'daily'
    RELEASE = 'release'


class PromoteMode(enum.Enum):
    MANIFESTS_ONLY = 'manifests_only'
    MANIFESTS_AND_PUBLISH = 'manifests_and_publish'


class ManifestType(enum.Enum):
    SINGLE = 'single'
    SET = 'set'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--flavourset', default='testing')
    parser.add_argument('--committish')
    parser.add_argument('--gardenlinux-epoch', type=int)
    parser.add_argument('--source', type=BuildType, default=BuildType.SNAPSHOT)
    parser.add_argument('--target', type=BuildType, default=BuildType.DAILY)
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--allow-partial', default=False, action='store_true')
    parser.add_argument(
        '--manifest-type',
        dest='manifest_types',
        default=[ManifestType.SET],
        action='append'
    )

    return parser.parse_args()


def promote(
    releases: typing.Sequence[glci.model.OnlineReleaseManifest],
    target_prefix: str,
    version_str: str,
    cicd_cfg: glci.model.CicdCfg,
    flavour_set: glci.model.GardenlinuxFlavourSet,
    manifest_types: typing.List[ManifestType]=tuple((ManifestType.SET,)),
):
    upload_release_manifest = glci.util.preconfigured(
        func=glci.util.upload_release_manifest,
        cicd_cfg=cicd_cfg,
    )
    upload_release_manifest_set = glci.util.preconfigured(
        func=glci.util.upload_release_manifest_set,
        cicd_cfg=cicd_cfg,
    )

    if ManifestType.SET in manifest_types:
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

    if ManifestType.SINGLE in manifest_types:
        for release in releases:
            manifest = release.stripped_manifest()
            flavour = manifest.flavour()

            manifest_path = os.path.join(
                target_prefix,
                f'{version_str}-{flavour.filename_prefix()}',
            )

            upload_release_manifest(
                key=manifest_path,
                manifest=manifest,
            )
            logger.info(f'promoted {manifest_path=}')


def main():
    parsed = parse_args()

    cicd_cfg = glci.util.cicd_cfg(cfg_name=parsed.cicd_cfg)
    build_cfg = cicd_cfg.build
    flavour_set = glci.util.flavour_set(flavour_set_name=parsed.flavourset)
    flavours = tuple(flavour_set.flavours())

    find_releases = glci.util.preconfigured(
        func=glci.util.find_releases,
        cicd_cfg=cicd_cfg,
    )

    releases = tuple(find_releases(
            flavour_set=flavour_set,
            build_committish=parsed.committish,
            gardenlinux_epoch=parsed.gardenlinux_epoch,
            prefix=build_cfg.manifest_key_prefix(name=parsed.source.value),
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
            'meta',
            parsed.target.value,
        ),
        version_str=str(parsed.gardenlinux_epoch),
        cicd_cfg=cicd_cfg,
        flavour_set=flavour_set,
        manifest_types=parsed.manifest_types,
    )

if __name__ == '__main__':
    main()
