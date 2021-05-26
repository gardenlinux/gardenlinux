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


def base_build_task():
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
        metadata=tkn.model.Metadata(name='base_build-gardenlinux-task'),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
            ],
        ),
    )
    return task


def _package_task(
    task_name: str,
    package_build_step: tkn.model.TaskStep,
    is_kernel_task: bool,
):
    cfssl_dir = NamedParam(
        name='cfssl_dir',
        default='/workspace/cfssl',
        description='git wokring dir to clone and build cfssl',
    )
    cfssl_fastpath = NamedParam(
        name='cfssl_fastpath',
         default='false',
        description='bypass cfssl build and copy binaries from github (set to true/false)',
    )
    cicd_cfg_name = NamedParam(
        name='cicd_cfg_name',
        default='default',
    )
    committish = NamedParam(
        name='committish',
        default='master',
        description='commit to build',
    )
    gardenlinux_build_deb_image = NamedParam(
        name='gardenlinux_build_deb_image',
        description='image to use for package build',
    )
    giturl = NamedParam(
        name='giturl',
        default='https://github.com/gardenlinux/gardenlinux.git',
        description='Gardenlinux Git repo',
    )

    if is_kernel_task:
        pkg_name = NamedParam(
            name='pkg_names',
            description='list of kernel-package to build (comma separated string)',
        )
    else:
        pkg_name = NamedParam(
            name='pkg_name',
            description='name of package to build',
        )

    repodir = NamedParam(
        name='repodir',
        default='/workspace/gardenlinux_git',
        description='Gardenlinux working dir',
    )
    s3_package_path = NamedParam(
        name='package_path_s3_prefix',
         default='packages',
        description='path relative to the root of the s3 bucket to upload the built packages to',
    )
    version_label = NamedParam(
        name='version_label',
        description='version label uses as tag for upload',
    )
    cfssl_committish = NamedParam(
        name='cfssl_committish',
        description='cfssl branch to clone',
        default='master'
    )
    cfss_git_url = NamedParam(
        name='cfssl_git_url',
        description='cfssl git url to clone',
        default='https://github.com/cloudflare/cfssl.git'
    )

    params = [
        cfssl_committish,
        cfss_git_url,
        cfssl_dir,
        cfssl_fastpath,
        cicd_cfg_name,
        committish,
        gardenlinux_build_deb_image,
        giturl,
        pkg_name,
        repodir,
        s3_package_path,
        version_label,
    ]

    clone_step_gl =  steps.clone_step(
        committish=committish,
        repo_dir=repodir,
        git_url=giturl,
    )

    clone_step_cfssl = steps.cfssl_clone_step(
        name='clone-step-cfssl',
        cfssl_committish=cfssl_committish,
        cfssl_dir=cfssl_dir,
        gardenlinux_repo_path_param=repodir,
        cfssl_git_url=cfss_git_url
    )

    cfssl_build_step = steps.build_cfssl_step()
    make_certs_step = steps.build_make_cert_step()
    s3_upload_packages_step = steps.build_upload_packages_step(
        cicd_cfg_name=cicd_cfg_name,
        repo_dir=repodir,
        s3_package_path=s3_package_path,
    )

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name=task_name),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step_gl,
                clone_step_cfssl,
                cfssl_build_step,
                make_certs_step,
                package_build_step,
                s3_upload_packages_step,
            ],
        ),
    )
    return task


def nokernel_package_task():
    return _package_task(
        task_name='build-packages',
        package_build_step=steps.build_package_step(),
        is_kernel_task=False,
    )


def kernel_package_task():
    return _package_task(
        task_name='build-kernel-packages',
        package_build_step=steps.build_kernel_package_step(),
        is_kernel_task=True,
    )
