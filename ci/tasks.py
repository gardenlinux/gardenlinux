import steps
import tkn.model


NamedParam = tkn.model.NamedParam

_giturl = NamedParam(name='giturl', default='ssh://git@github.com/gardenlinux/gardenlinux')
_repodir = NamedParam(name='repodir', default='/workspace/gardenlinux_git')


def promote_task(
    branch: NamedParam,
    committish: NamedParam,
    gardenlinux_epoch: NamedParam,
    snapshot_timestamp: NamedParam,
    cicd_cfg_name: NamedParam,
    version: NamedParam,
    flavourset: NamedParam,
    promote_target: NamedParam,
    promote_mode: NamedParam,
    repodir: NamedParam=_repodir,
    giturl: NamedParam=_giturl,
    name='promote-gardenlinux-task',
    namespace='gardenlinux-tkn',
):
    clone_step = steps.clone_step(
        committish=committish,
        repo_dir=repodir,
        git_url=giturl,
    )

    promote_step = steps.promote_step(
        cicd_cfg_name=cicd_cfg_name,
        flavourset=flavourset,
        promote_target=promote_target,
        promote_mode=promote_mode,
        gardenlinux_epoch=gardenlinux_epoch,
        committish=committish,
        version=version,
        repo_dir=repodir,
    )

    release_step = steps.release_step(
        giturl=giturl,
        branch=branch,
        gardenlinux_epoch=gardenlinux_epoch,
        promote_mode=promote_mode,
        repo_dir=repodir,
    )

    params = [
        giturl,
        branch,
        committish,
        gardenlinux_epoch,
        snapshot_timestamp,
        cicd_cfg_name,
        version,
        flavourset,
        promote_target,
        promote_mode,
        repodir,
    ]

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name=name, namespace=namespace),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
                promote_step,
                release_step,
            ],
        ),
    )
    return task


def build_task(
    namespace: str='gardenlinux-tkn',
):
    suite = NamedParam(name='suite', default='bullseye')
    arch = NamedParam(name='architecture', default='amd64')
    mods = NamedParam(name='modifiers')
    giturl = NamedParam(name='giturl', default='ssh://git@github.com/gardenlinux/gardenlinux')
    committish = NamedParam(name='committish', default='master')
    glepoch = NamedParam(name='gardenlinux_epoch')
    snapshot_ts = NamedParam(name='snapshot_timestamp')
    repodir = NamedParam(name='repodir', default='/workspace/gardenlinux_git')
    cicd_cfg_name = NamedParam(name='cicd_cfg_name', default='default')
    outfile = NamedParam(name='outfile', default='/workspace/gardenlinux.out')

    params = [
        suite,
        arch,
        mods,
        giturl,
        committish,
        glepoch,
        snapshot_ts,
        repodir,
        cicd_cfg_name,
        outfile,
    ]

    clone_step = steps.clone_step(
        committish=committish,
        repo_dir=repodir,
        git_url=giturl,
    )

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name='build-gardenlinux-task', namespace=namespace),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
            ],
        ),
    )

    return task
