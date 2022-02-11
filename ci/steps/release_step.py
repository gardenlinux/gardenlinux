import logging
import sys

import github_release
import glci.model
import release

parsable_to_int = str

logger = logging.getLogger(__name__)


def release_step(
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    ctx_repository_config_name: str,
    flavour_set_name: str,
    gardenlinux_epoch: parsable_to_int,
    giturl: str,
    repo_dir: str,
    version: str,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if not glci.model.BuildTarget.GITHUB_RELEASE in build_target_set:
      logger.info(f'{build_target_set=} - will not perform release')
      return

    print(f'Making release for {committish=}')

    release.ensure_target_branch_exists(
        release_branch=release.release_branch_name(gardenlinux_epoch=gardenlinux_epoch),
        release_committish=committish,
        release_version=glci.model.next_release_version_from_workingtree(epoch=gardenlinux_epoch)[0],
        git_helper=release._git_helper(giturl=giturl),
        giturl=giturl,
    )

    # Make the github release
    release_created = github_release.make_release(
        cicd_cfg_name=cicd_cfg_name,
        committish=committish,
        ctx_repository_config_name=ctx_repository_config_name,
        flavour_set_name=flavour_set_name,
        gardenlinux_epoch=gardenlinux_epoch,
        giturl=giturl,
        repo_dir=repo_dir,
        version=version,
    )

    sys.exit(0 if release_created else 1)
