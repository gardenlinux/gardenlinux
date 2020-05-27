import steps
import tkn.model


NamedParam = tkn.model.NamedParam

_giturl = NamedParam(name='giturl', default='ssh://git@github.com/gardenlinux/gardenlinux')
_repodir = NamedParam(name='repodir', default='/workspace/gardenlinux_git')


def promote_task(
    committish: NamedParam,
    gardenlinux_epoch: NamedParam,
    snapshot_timestamp: NamedParam,
    cicd_cfg_name: NamedParam,
    version: NamedParam,
    flavourset: NamedParam,
    promote_target: NamedParam,
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

    params = [
        giturl,
        committish,
        gardenlinux_epoch,
        snapshot_timestamp,
        cicd_cfg_name,
        version,
        flavourset,
        promote_target,
        repodir,
    ]

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name=name, namespace=namespace),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
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
    fnamep = NamedParam(name='fnameprefix')
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
        fnamep,
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
