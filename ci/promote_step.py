import dataclasses
import datetime
import io
import os
import sys

import hashlib
import yaml

import glci.model
import glci.util
import promote

parsable_to_int = str


def promote_step(
    cicd_cfg_name: str,
    flavourset: str,
    promote_target: str,
    gardenlinux_epoch: parsable_to_int,
    committish: str,
    version: str,
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    build_cfg = cicd_cfg.build
    flavour_set = glci.util.flavour_set(flavourset)
    flavours = tuple(flavour_set.flavours())

    find_releases = glci.util.preconfigured(
      func=glci.util.find_releases,
      cicd_cfg=cicd_cfg,
    )

    release_target = promote_target
    release_source = 'snapshots' # unhardcode

    releases = tuple(
      find_releases(
        flavour_set=flavour_set,
        build_committish=committish,
        version=version,
        gardenlinux_epoch=int(gardenlinux_epoch),
        prefix=build_cfg.manifest_key_prefix(name=release_source),
      )
    )

    # ensure all previous tasks really were successful
    is_complete = len(releases) == len(flavours)
    if not is_complete:
      print('release was not complete - will not promote (this indicates a bug!)')
      sys.exit(1) # do not signal an error

    # if this line is reached, the release has been complete
    promote.promote(
      releases=releases,
      target_prefix=os.path.join(
        'meta',
        release_target,
      ),
      cicd_cfg=cicd_cfg,
      flavour_set=flavour_set,
      version_str=version,
    )
