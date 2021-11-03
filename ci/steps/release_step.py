import glci.model
import release

parsable_to_int = str


def release_step(
    giturl: str,
    committish: str,
    gardenlinux_epoch: parsable_to_int,
    build_targets: str,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if not glci.model.BuildTarget.GITHUB_RELEASE in build_target_set:
      print(f'{build_target_set=} - will not perform release')
      return

    release.ensure_target_branch_exists(
        release_branch=release.release_branch_name(gardenlinux_epoch=gardenlinux_epoch),
        release_committish=committish,
        release_version=glci.model.next_release_version_from_workingtree(),
        git_helper=release._git_helper(giturl=giturl),
        giturl=giturl,
    )
