import steps
import tkn.model


NamedParam = tkn.model.NamedParam

_giturl = NamedParam(name='giturl', default='ssh://git@github.com/gardenlinux/gardenlinux')
_repodir = NamedParam(name='repodir', default='/workspace/gardenlinux_git')


def promote_task(
    branch: NamedParam,
    cicd_cfg_name: NamedParam,
    committish: NamedParam,
    flavourset: NamedParam,
    gardenlinux_epoch: NamedParam,
    publishing_actions: NamedParam,
    snapshot_timestamp: NamedParam,
    version: NamedParam,
    env_vars=[],
    giturl: NamedParam = _giturl,
    name='promote-gardenlinux-task',
    repodir: NamedParam = _repodir,
    volume_mounts=[],
):

    clone_step = steps.clone_step(
        committish=committish,
        env_vars=env_vars,
        git_url=giturl,
        repo_dir=repodir,
        volume_mounts=volume_mounts,
    )

    promote_step = steps.promote_step(
        cicd_cfg_name=cicd_cfg_name,
        committish=committish,
        env_vars=env_vars,
        flavourset=flavourset,
        gardenlinux_epoch=gardenlinux_epoch,
        publishing_actions=publishing_actions,
        repo_dir=repodir,
        version=version,
        volume_mounts=volume_mounts,
    )

    release_step = steps.release_step(
        committish=committish,
        env_vars=env_vars,
        gardenlinux_epoch=gardenlinux_epoch,
        giturl=giturl,
        publishing_actions=publishing_actions,
        repo_dir=repodir,
        volume_mounts=volume_mounts,
    )

    params = [
        branch,
        cicd_cfg_name,
        committish,
        flavourset,
        gardenlinux_epoch,
        giturl,
        publishing_actions,
        repodir,
        snapshot_timestamp,
        version,
    ]

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name=name),
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
    use_secrets_server: bool,
):
    arch = NamedParam(name='architecture', default='amd64')
    cicd_cfg_name = NamedParam(name='cicd_cfg_name', default='default')
    committish = NamedParam(name='committish', default='master')
    giturl = NamedParam(name='giturl', default='ssh://git@github.com/gardenlinux/gardenlinux')
    glepoch = NamedParam(name='gardenlinux_epoch')
    mods = NamedParam(name='modifiers')
    outfile = NamedParam(name='outfile', default='/workspace/gardenlinux.out')
    repodir = NamedParam(name='repodir', default='/workspace/gardenlinux_git')
    snapshot_ts = NamedParam(name='snapshot_timestamp')
    suite = NamedParam(name='suite', default='bullseye')

    params = [
        arch,
        cicd_cfg_name,
        committish,
        giturl,
        glepoch,
        mods,
        outfile,
        repodir,
        snapshot_ts,
        suite,
    ]

    if use_secrets_server:
        env_vars = [{
            'name': 'SECRETS_SERVER_CACHE',
            'value': '/secrets/config.json',
        }]
        volume_mounts = [{
            'name': 'secrets',
            'mountPath': '/secrets',
        }]
    else:
        env_vars = []
        volume_mounts = []

    clone_step = steps.clone_step(
        committish=committish,
        env_vars=env_vars,
        git_url=giturl,
        repo_dir=repodir,
        volume_mounts=volume_mounts,
    )

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name='build-gardenlinux-task'),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
            ],
        ),
    )
    return task

def base_build_task(
    namespace: str='gardenlinux',
):
    giturl = NamedParam(name='giturl', default='ssh://git@github.com/gardenlinux/gardenlinux')
    committish = NamedParam(name='committish', default='master')
    glepoch = NamedParam(name='gardenlinux_epoch')
    snapshot_ts = NamedParam(name='snapshot_timestamp')
    repodir = NamedParam(name='repodir', default='/workspace/gardenlinux_git')
    params = [
        giturl,
        committish,
        glepoch,
        snapshot_ts,
        repodir,
    ]

    clone_step = steps.clone_step(
        committish=committish,
        repo_dir=repodir,
        git_url=giturl,
    )
    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name='base_build-gardenlinux-task', namespace=namespace),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
            ],
        ),
    )
    return task
