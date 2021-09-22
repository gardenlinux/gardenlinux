import enum
import os
import typing

import params
import tkn.model

IMAGE_VERSION = '1.1477.0'
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
    params: params.AllParams,
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
                params.committish,
                params.giturl,
                params.repo_dir,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )

    return step


def cfssl_clone_step(
    name: str,
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )

    return step


def upload_results_step(
    params: params.AllParams,
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
                params.architecture,
                params.cicd_cfg_name,
                params.committish,
                params.gardenlinux_epoch,
                params.modifiers,
                params.outfile,
                params.platform,
                params.publishing_actions,
                params.version,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def promote_single_step(
    params: params.AllParams,
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
                params.architecture,
                params.cicd_cfg_name,
                params.committish,
                params.gardenlinux_epoch,
                params.modifiers,
                params.platform,
                params.publishing_actions,
                params.version,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def promote_step(
    params: params.AllParams,
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
                params.cicd_cfg_name,
                params.committish,
                params.flavourset,
                params.gardenlinux_epoch,
                params.publishing_actions,
                params.version,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def pre_build_step(
    params: params.AllParams,
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
                params.architecture,
                params.cicd_cfg_name,
                params.committish,
                params.gardenlinux_epoch,
                params.modifiers,
                params.platform,
                params.publishing_actions,
                params.version,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def release_step(
    params: params.AllParams,
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
                params.committish,
                params.gardenlinux_epoch,
                params.giturl,
                params.publishing_actions,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_cfssl_step(
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
            params=[
                # !DO NOT CHANGE ORDER!
                params.repo_dir,
                params.cfssl_fastpath,
                params.cfssl_dir,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def write_key_step(
    params: params.AllParams,
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
                params.repo_dir,
                params.key_config_name,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_cert_step(
    params: params.AllParams,
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
                params.repo_dir,
            ],
            repo_path_param=params.repo_dir,
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_package_step(
    params: params.AllParams,
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
                params.repo_dir,
                params.pkg_name,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_kernel_package_step(
    params: params.AllParams,
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
                params.repo_dir,
                params.pkg_names,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_upload_packages_step(
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
            params=[
                params.cicd_cfg_name,
                params.s3_package_path,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_publish_packages_repository_step(
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
            params=[
                params.cicd_cfg_name,
                params.s3_package_path,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def build_image_step(
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
            params=[
                # !DO NOT CHANGE ORDER!
                params.suite,
                params.gardenlinux_epoch,
                params.snapshot_timestamp,
                params.platform,
                params.modifiers,
                params.architecture,
                params.committish,
                params.version
            ],
        ),
        volumeMounts=build_image_step_volume_mounts,
        env=env_vars,
        resources=build_image_step_resource_config,
        securityContext=build_image_step_security_context,
    )


def build_base_image_step(
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
            params=[
                params.oci_path,
                params.repo_dir,
                params.version_label,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def create_component_descriptor_step(
    params: params.AllParams,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='component-descriptor',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'component_descriptor.py'),
            script_type=ScriptType.PYTHON3,
            callable='build_component_descriptor',
            repo_path_param=params.repo_dir,
            params=[
                params.branch,
                params.cicd_cfg_name,
                params.committish,
                params.ctx_repository_config_name,
                params.gardenlinux_epoch,
                params.publishing_actions,
                params.snapshot_ctx_repository_config_name,
                params.version,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def notify_step(
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
            params=[
                params.additional_recipients,
                params.cicd_cfg_name,
                params.disable_notifications,
                params.giturl,
                params.namespace,
                params.only_recipients,
                params.pipeline_name,
                params.pipeline_run_name,
                params.repo_dir,
                params.status_dict_str,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def get_logs_step(
    params: params.AllParams,
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
            repo_path_param=params.repo_dir,
            params=[
                params.repo_dir,
                params.pipeline_run_name,
                params.namespace,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def pre_check_tests_step(
    params: params.AllParams,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='pre-check-tests',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'pre_check_tests.py'),
            script_type=ScriptType.PYTHON3,
            callable='pre_check_tests',
            repo_path_param=params.repo_dir,
            params=[
                params.architecture,
                params.cicd_cfg_name,
                params.committish,
                params.gardenlinux_epoch,
                params.modifiers,
                params.platform,
                params.publishing_actions,
                params.version,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def test_step(
    params: params.AllParams,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='run-tests',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'run_tests.py'),
            script_type=ScriptType.PYTHON3,
            callable='run_tests',
            repo_path_param=params.repo_dir,
            params=[
                params.architecture,
                params.cicd_cfg_name,
                params.committish,
                params.gardenlinux_epoch,
                params.modifiers,
                params.platform,
                params.publishing_actions,
                params.repo_dir,
                params.snapshot_timestamp,
                params.suite,
                params.version,
                params.pytest_cfg,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def upload_test_results_step(
    params: params.AllParams,
    env_vars: typing.List[typing.Dict] = [],
    volume_mounts: typing.List[typing.Dict] = [],
):
    return tkn.model.TaskStep(
        name='upload-test-results',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'upload_test_results.py'),
            script_type=ScriptType.PYTHON3,
            callable='upload_test_results',
            repo_path_param=params.repo_dir,
            params=[
                params.architecture,
                params.cicd_cfg_name,
                params.committish,
                params.gardenlinux_epoch,
                params.modifiers,
                params.platform,
                params.publishing_actions,
                params.repo_dir,
                params.version,
            ],
        ),
        volumeMounts=volume_mounts,
        env=env_vars,
    )


def attach_log_step(
        params: params.AllParams,
        env_vars: typing.List[typing.Dict] = [],
        volume_mounts: typing.List[typing.Dict] = [],
    ):
    return tkn.model.TaskStep(
        name='upload-logs-step',
        image=DEFAULT_IMAGE,
        script=task_step_script(
            path=os.path.join(steps_dir, 'attach_logs.py'),
            script_type=ScriptType.PYTHON3,
            callable='upload_logs',
            repo_path_param=params.repo_dir,
            params=[
                params.architecture,
                params.cicd_cfg_name,
                params.committish,
                params.gardenlinux_epoch,
                params.modifiers,
                params.namespace,
                params.pipeline_run_name,
                params.platform,
                params.repo_dir,
                params.version,
            ],
        ),
    volumeMounts=volume_mounts,
    env=env_vars,
    )
