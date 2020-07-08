import glci.model
import promote
import release

parsable_to_int = str

def release_step(
    giturl: str,
    branch: str,
    gardenlinux_epoch: parsable_to_int,
    publishing_actions: str,
):
    publishing_actions = [
        glci.model.PublishAction(action.strip()) for action in publishing_actions.split(',')
    ]

    if not glci.model.PublishingAction.RELEASE in publishing_actions:
      print(f'{publishing_actions=} - will not perform release')
      return

    release.ensure_target_branch_exists(
        source_branch=branch,
        release_branch=release.release_branch_name(gardenlinux_epoch=gardenlinux_epoch),
        release_version=glci.model.next_release_version_from_workingtree(),
        git_helper=release._git_helper(giturl=giturl),
        giturl=giturl,
    )
