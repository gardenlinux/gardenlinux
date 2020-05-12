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


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--flavourset', default='testing')
    parser.add_argument('--committish')
    parser.add_argument('--gardenlinux-epoch', type=int)
    parser.add_argument('--source', type=BuildType, default=BuildType.SNAPSHOT)
    parser.add_argument('--target', type=BuildType, default=BuildType.DAILY)
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--allow-partial', default=False, action='store_true')

    return parser.parse_args()


def promote(
    releases: typing.Sequence[glci.model.OnlineReleaseManifest],
    target_prefix: str,
    version_str: str,
    cicd_cfg: glci.model.CicdCfg,
):
    upload_release_manifest = glci.util.preconfigured(
        func=glci.util.upload_release_manifest,
        cicd_cfg=cicd_cfg,
    )

    for release in releases:
        manifest = release.stripped_manifest()
        flavour = manifest.flavour()

        manifest_path = os.path.join(
            target_prefix,
            f'{flavour.filename_prefix()}-{version_str}',
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

    if not is_complete:
        logger.warning('Release is not complete')
        if not parsed.allow_partial:
            logger.error(f'{parsed.allow_partial=} -> aborting')
            sys.exit(1)

    logger.info(f'found {len(releases)} matching release(s) {is_complete=}')
    promote(
        releases=releases,
        target_prefix=os.path.join(
            'meta',
            parsed.target.value,
        ),
        version_str=str(parsed.gardenlinux_epoch),
        cicd_cfg=cicd_cfg,
    )

if __name__ == '__main__':
    main()
