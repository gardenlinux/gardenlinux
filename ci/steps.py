import enum
import os
import typing

import tkn.model

IMAGE_VERSION = '1.1388.0'
DEFAULT_IMAGE = f'eu.gcr.io/gardener-project/cc/job-image:{IMAGE_VERSION}'
KANIKO_IMAGE = f'eu.gcr.io/gardener-project/cc/job-image-kaniko:{IMAGE_VERSION}'

own_dir = os.path.abspath(os.path.dirname(__file__))
scripts_dir = os.path.join(own_dir)
steps_dir = os.path.join(own_dir, 'steps')


def extend_python_path_snippet(param_name: str):
    sd_name = os.path.basename(scripts_dir)
    return f'sys.path.insert(1,os.path.abspath(os.path.join("$(params.{param_name})","{sd_name}")))'


class ScriptType(enum.Enum):
    BOURNE_SHELL = 'sh'
    PYTHON3 = 'python3'


def task_step_script(
    script_type: ScriptType,
    callable: str,
    params: typing.List[tkn.model.NamedParam],
    repo_path_param: typing.Optional[tkn.model.NamedParam]=None,
    path: str = None,
    inline_script: str = None,
):
    '''
    renders an inline-step-script, prepending a shebang, and appending an invocation
    of the specified callable (passing the given params). Either use path to inline
    script from a file or use inline inline_script to pass script directly

    '''

    if path and inline_script:
        raise ValueError("Either use path or inline_script but not both.")

    if path:
        with open(path) as f:
            script = f.read()
    elif inline_script:
        script = inline_script

    if script_type is ScriptType.PYTHON3:
        shebang = '#!/usr/bin/env python3'
        if repo_path_param:
            preamble = 'import sys,os;' + extend_python_path_snippet(repo_path_param.name)
        else:
            preamble = ''

        args = ','.join((
            f"{param.name.replace('-', '_')}='$(params.{param.name})'" for param in params
        ))
        callable_str = f'{callable}({args})'
    elif script_type is ScriptType.BOURNE_SHELL:
        shebang = '#!/usr/bin/env bash'
        preamble = ''
        args = ' '.join([f'"$(params.{param.name})"' for param in params])
        callable_str = f'{callable} {args}'

    if callable:
        return '\n'.join((
            shebang,
            preamble,
            script,
            callable_str,
        ))
    else:
        return '\n'.join((
            shebang,
            preamble,
            script,
        ))


def clone_step(
    committish: tkn.model.NamedParam,
    git_url: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    step = tkn.model.TaskStep(
        name='clone-repo-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'clone_repo_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='clone_and_copy',
            params=[
                committish,
                git_url,
                repo_dir,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )

    return step


def cfssl_clone_step(
    name: str,
    committish: tkn.model.NamedParam,
    git_url: tkn.model.NamedParam,
    working_dir: tkn.model.NamedParam,
    gardenlinux_repo_path_param: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    step = tkn.model.TaskStep(
        name=name,
        image=DEFAULT_IMAGE,
        script=task_step_script(
            script_type=ScriptType.PYTHON3,
            path=os.path.join(steps_dir, 'clone_simple_step.py'),
            callable="git_clone('$(params.cfssl_git_url)', '$(params.cfssl_committish)', "
                     "'$(params.cfssl_dir)'); dummy",
            params=[],
            repo_path_param=gardenlinux_repo_path_param,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )

    return step


def upload_results_step(
    architecture: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    outfile: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='upload-results',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'upload_results_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='upload_results_step',
            params=[
                architecture,
                cicd_cfg_name,
                committish,
                gardenlinux_epoch,
                modifiers,
                outfile,
                platform,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def promote_single_step(
    architecture: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='promote-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'promote_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='promote_single_step',
            params=[
                architecture,
                cicd_cfg_name,
                committish,
                gardenlinux_epoch,
                modifiers,
                platform,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def promote_step(
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    flavourset: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='finalise-promotion-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'promote_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='promote_step',
            params=[
                cicd_cfg_name,
                committish,
                flavourset,
                gardenlinux_epoch,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def pre_build_step(
    architecture: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    version: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='prebuild-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'pre_build_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='pre_build_step',
            params=[
                architecture,
                cicd_cfg_name,
                committish,
                gardenlinux_epoch,
                modifiers,
                platform,
                publishing_actions,
                version,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def release_step(
    committish: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    giturl: tkn.model.NamedParam,
    publishing_actions: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='release-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'release_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='release_step',
            params=[
                committish,
                gardenlinux_epoch,
                giturl,
                publishing_actions,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_cfssl_step(
    repo_dir: tkn.model.NamedParam,
    cfssl_fastpath: tkn.model.NamedParam,
    cfssl_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='build-cfssl-step',
        image='golang:latest',
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_cfssl.sh'),
            script_type=ScriptType.BOURNE_SHELL,
            callable='build_cfssl',
            repo_path_param=repo_dir,
            params=[
                # !DO NOT CHANGE ORDER!
                repo_dir,
                cfssl_fastpath,
                cfssl_dir,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def write_key_step(
    repo_dir: tkn.model.NamedParam,
    key_config_name: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='write-key',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'write_key.py'),
            script_type=ScriptType.PYTHON3,
            callable='write_key',
            params=[
                repo_dir,
                key_config_name,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_cert_step(
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='build-cert',
        image='golang:latest',
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_cert.sh'),
            script_type=ScriptType.BOURNE_SHELL,
            callable='build_cert',
            params=[
                repo_dir,
            ],
            repo_path_param=repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_package_step(
    repo_dir: tkn.model.NamedParam,
    package_name: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='build-package',
        image='$(params.gardenlinux_build_deb_image)',
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_package.sh'),
            script_type=ScriptType.BOURNE_SHELL,
            callable='build_package',
            params=[
                repo_dir,
                package_name,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_kernel_package_step(
    repo_dir: tkn.model.NamedParam,
    package_names: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='build-package',
        image='$(params.gardenlinux_build_deb_image)',
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_kernel_package.sh'),
            script_type=ScriptType.BOURNE_SHELL,
            callable='build_kernel_package',
            params=[
                repo_dir,
                package_names,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_upload_packages_step(
    repo_dir: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    s3_package_path: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='upload-packages-s3',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'upload_packages.py'),
            script_type=ScriptType.PYTHON3,
            callable='upload_packages',
            repo_path_param=repo_dir,
            params=[
                cicd_cfg_name,
                s3_package_path,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_publish_packages_repository_step(
    cicd_cfg_name: tkn.model.NamedParam,
    s3_package_path: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='publish-package-repository-s3',
        image='$(params.gardenlinux_build_deb_image)',
        script=task_step_script(
            path=os.path.join(steps_dir, 'publish_package_repository.py'),
            script_type=ScriptType.PYTHON3,
            callable='main',
            repo_path_param=repo_dir,
            params=[
                cicd_cfg_name,
                s3_package_path,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_image_step(
    repo_dir: tkn.model.NamedParam,
    suite: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    timestamp: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    arch: tkn.model.NamedParam,
    committish: tkn.model.NamedParam,
    gardenversion: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    build_image_step_volume_mounts = [vm for vm in volume_mounts]
    build_image_step_volume_mounts.extend([{
        'mountPath': '/dev',
        'name': 'dev',
    }, {
        'mountPath': '/build',
        'name': 'build',
    }])

    build_image_step_resource_config = {
        'requests': {
            'memory': '1Gi',
        },
        'limits': {
            'memory': '1.5Gi',
        },
    }
    build_image_step_security_context = {
        'privileged': True,
        'allowPrivilegeEscalation': True,
        'capabilities': {
          'add': ['SYS_ADMIN'],
        },
    }
    return tkn.model.TaskStep(
        name='build-image',
        image='$(params.build_image)',
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_image.sh'),
            script_type=ScriptType.BOURNE_SHELL,
            callable='build_image',
            repo_path_param=repo_dir,
            params=[
                # !DO NOT CHANGE ORDER!
                suite,
                gardenlinux_epoch,
                timestamp,
                platform,
                modifiers,
                arch,
                committish,
                gardenversion
            ],
        ),
        volumeMounts=build_image_step_volume_mounts,
        env=env_vars,
        resources=build_image_step_resource_config,
        securityContext=build_image_step_security_context,
    )


def build_base_image_step(
    repo_dir: tkn.model.NamedParam,
    oci_path: tkn.model.NamedParam,
    version_label: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='basebuild',
        image=KANIKO_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'build_base_image.py'),
            script_type=ScriptType.PYTHON3,
            callable='build_base_image',
            repo_path_param=repo_dir,
            params=[
                oci_path,
                repo_dir,
                version_label,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def notify_step(
    additional_recipients: tkn.model.NamedParam,
    cicd_cfg_name: tkn.model.NamedParam,
    disable_notifications: tkn.model.NamedParam,
    git_url: tkn.model.NamedParam,
    namespace: tkn.model.NamedParam,
    only_recipients: tkn.model.NamedParam,
    pipeline_name: tkn.model.NamedParam,
    pipeline_run_name: tkn.model.NamedParam,    
    repo_dir: tkn.model.NamedParam,
    status_dict_str: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='notify-status',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'notify.py'),
            script_type=ScriptType.PYTHON3,
            callable='send_notification',
            repo_path_param=repo_dir,
            params=[
                additional_recipients,
                cicd_cfg_name,
                disable_notifications,
                git_url,
                namespace,
                only_recipients,
                pipeline_name,
                pipeline_run_name,
                repo_dir,
                status_dict_str,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def get_logs_step(
    repo_dir: tkn.model.NamedParam,
    pipeline_run_name: tkn.model.NamedParam,
    namespace: tkn.model.NamedParam,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='get-logs',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'get_logs.py'),
            script_type=ScriptType.PYTHON3,
            callable='getlogs',
            repo_path_param=repo_dir,
            params=[
                repo_dir,
                pipeline_run_name,
                namespace,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )
