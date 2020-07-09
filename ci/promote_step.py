import os
import sys

import glci.model
import glci.util
import promote

parsable_to_int = str


def promote_step(
    cicd_cfg_name: str,
    flavourset: str,
    promote_target: str,
    publishing_actions: str,
    gardenlinux_epoch: parsable_to_int,
    committish: str,
    version: str,
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    flavour_set = glci.util.flavour_set(flavourset)
    flavours = tuple(flavour_set.flavours())
    publishing_actions = [
        glci.model.PublishingAction(action.strip()) for action in publishing_actions.split(',')
    ]

    find_releases = glci.util.preconfigured(
      func=glci.util.find_releases,
      cicd_cfg=cicd_cfg,
    )

    release_target = promote_target

    releases = tuple(
      find_releases(
        flavour_set=flavour_set,
        build_committish=committish,
        version=version,
        gardenlinux_epoch=int(gardenlinux_epoch),
        prefix=glci.model.ReleaseManifest.manifest_key_prefix,
      )
    )

    # ensure all previous tasks really were successful
    is_complete = len(releases) == len(flavours)
    if not is_complete:
      print('release was not complete - will not promote (this indicates a bug!)')
      sys.exit(1) # do not signal an error

    print(publishing_actions)

    # if this line is reached, the release has been complete

    promote.promote(
      gardenlinux_epoch=gardenlinux_epoch,
      build_committish=committish,
      releases=releases,
      target_prefix=os.path.join(
        'meta',
        release_target,
      ),
      publishing_actions=publishing_actions,
      cicd_cfg=cicd_cfg,
      flavour_set=flavour_set,
      version_str=version,
      build_type=glci.model.BuildType(promote_target),
    )
