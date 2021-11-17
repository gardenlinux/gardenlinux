import github_release
import glci.model
import release

parsable_to_int = str


def release_step(
    build_targets: str,
    cicd_cfg_name: str,
    committish: str,
    ctx_repository_config_name: str,
    flavourset: str,
    gardenlinux_epoch: parsable_to_int,
    giturl: str,
    repo_dir: str,
    version: str,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if not glci.model.BuildTarget.GITHUB_RELEASE in build_target_set:
      print(f'{build_target_set=} - will not perform release')
      return

    print(f'Making release for {committish=}')

    release.ensure_target_branch_exists(
        release_branch=release.release_branch_name(gardenlinux_epoch=gardenlinux_epoch),
        release_committish=committish,
        release_version=glci.model.next_release_version_from_workingtree(epoch=gardenlinux_epoch),
        git_helper=release._git_helper(giturl=giturl),
        giturl=giturl,
    )

    # Make the github release
    github_release.make_release(
        cicd_cfg_name=cicd_cfg_name,
        committish=committish,
        ctx_repository_config_name=ctx_repository_config_name,
        flavourset_name=flavourset,
        gardenlinux_epoch=gardenlinux_epoch,
        giturl=giturl,
        repo_dir=repo_dir,
        version=version,
    )
