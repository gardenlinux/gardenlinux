import params
import steps
import tkn.model

NamedParam = tkn.model.NamedParam

all_params = params.AllParams


def promote_task(
    name='promote-gardenlinux-task',
    env_vars=[],
    volumes=[],
    volume_mounts=[],
):

    clone_step = steps.clone_step(
        params=all_params,
        volume_mounts=volume_mounts,
    )

    promote_step = steps.promote_step(
        params=all_params,
        volume_mounts=volume_mounts,
    )

    release_step = steps.release_step(
        params=all_params,
        volume_mounts=volume_mounts,
    )

    build_cd_step = steps.create_component_descriptor_step(
        params=all_params,
        volume_mounts=volume_mounts,
    )

    params = [
        all_params.branch,
        all_params.cicd_cfg_name,
        all_params.ctx_repository_config_name,
        all_params.snapshot_ctx_repository_config_name,
        all_params.committish,
        all_params.flavourset,
        all_params.gardenlinux_epoch,
        all_params.giturl,
        all_params.publishing_actions,
        all_params.repo_dir,
        all_params.snapshot_timestamp,
        all_params.version,
    ]

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name=name),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
                build_cd_step,
                promote_step,
                release_step,
            ],
            volumes=volumes,
        ),
    )
    return task


def _package_task(
    task_name: str,
    package_build_step: tkn.model.TaskStep,
    is_kernel_task: bool,
    env_vars,
    volumes,
    volume_mounts,
):

    if is_kernel_task:
        pkg_name = all_params.pkg_names
    else:
        pkg_name = all_params.pkg_name

    params = [
        all_params.cfss_git_url,
        all_params.cfssl_committish,
        all_params.cfssl_dir,
        all_params.cfssl_fastpath,
        all_params.cicd_cfg_name,
        all_params.committish,
        all_params.gardenlinux_build_deb_image,
        all_params.giturl,
        all_params.key_config_name,
        pkg_name,
        all_params.repo_dir,
        all_params.s3_package_path,
        all_params.version_label,
    ]

    clone_step_gl = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    clone_step_cfssl = steps.cfssl_clone_step(
        name='clone-step-cfssl',
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    write_key_step = steps.write_key_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    cfssl_build_step = steps.build_cfssl_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    build_certs_step = steps.build_cert_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    s3_upload_packages_step = steps.build_upload_packages_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name=task_name),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step_gl,
                clone_step_cfssl,
                write_key_step,
                cfssl_build_step,
                build_certs_step,
                package_build_step,
                s3_upload_packages_step,
            ],
            volumes=volumes,
        ),
    )
    return task


def nokernel_package_task(
    env_vars,
    volumes,
    volume_mounts,
):
    return _package_task(
        task_name='build-packages',
        package_build_step=steps.build_package_step(
            params=all_params,
        ),
        is_kernel_task=False,
        env_vars=env_vars,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )


def kernel_package_task(
    env_vars,
    volumes,
    volume_mounts,
):
    return _package_task(
        task_name='build-kernel-packages',
        package_build_step=steps.build_kernel_package_step(
            params=all_params,
        ),
        is_kernel_task=True,
        env_vars=env_vars,
        volumes=volumes,
        volume_mounts=volume_mounts,
    )


def build_task(
    env_vars,
    volume_mounts,
    volumes=[],
):
    clone_step = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    pre_build_step = steps.pre_build_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    build_image_step = steps.build_image_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    upload_step = steps.upload_results_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    task_volumes = [v for v in volumes]
    task_volumes.extend(
        [{
            'name': 'dev',
            'hostPath': {'path': '/dev', 'type': 'Directory'},
        }, {
            'name': 'build',
            'emptyDir': {'medium': 'Memory'},
        }]
    )

    return tkn.model.Task(
        metadata=tkn.model.Metadata(name='build-gardenlinux-task'),
        spec=tkn.model.TaskSpec(
            params=[
                all_params.architecture,
                all_params.build_image,
                all_params.cicd_cfg_name,
                all_params.committish,
                all_params.flavourset,
                all_params.giturl,
                all_params.gardenlinux_epoch,
                all_params.modifiers,
                all_params.outfile,
                all_params.platform,
                all_params.promote_target,
                all_params.publishing_actions,
                all_params.repo_dir,
                all_params.snapshot_timestamp,
                all_params.suite,
                all_params.version,
            ],
            steps=[
                clone_step,
                pre_build_step,
                build_image_step,
                upload_step,
            ],
            volumes=task_volumes,
        ),
    )


def test_task(
    env_vars,
    volume_mounts,
    volumes=[],
):
    clone_step = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    pre_check_tests_step = steps.pre_check_tests_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    test_step = steps.test_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    upload_test_results_step = steps.upload_test_results_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    task_volumes = [v for v in volumes]
    task_volumes.extend(
        [{
            'name': 'dev',
            'hostPath': {'path': '/dev', 'type': 'Directory'},
        }, {
            'name': 'build',
            'emptyDir': {'medium': 'Memory'},
        }]
    )

    return tkn.model.Task(
        metadata=tkn.model.Metadata(name='integration-test-task'),
        spec=tkn.model.TaskSpec(
            params=[
                all_params.architecture,
                all_params.build_image,
                all_params.cicd_cfg_name,
                all_params.committish,
                all_params.flavourset,
                all_params.giturl,
                all_params.gardenlinux_epoch,
                all_params.modifiers,
                all_params.outfile,
                all_params.platform,
                all_params.promote_target,
                all_params.publishing_actions,
                all_params.repo_dir,
                all_params.snapshot_timestamp,
                all_params.suite,
                all_params.version,
                all_params.pytest_cfg,
            ],
            steps=[
                clone_step,
                pre_check_tests_step,
                test_step,
                upload_test_results_step,
            ],
            volumes=task_volumes,
        ),
    )


def base_image_build_task(env_vars, volumes, volume_mounts):
    clone_repo_step = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    build_base_image_step = steps.build_base_image_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    return tkn.model.Task(
        metadata=tkn.model.Metadata(name='build-baseimage'),
        spec=tkn.model.TaskSpec(
            params=[
                all_params.committish,
                all_params.giturl,
                all_params.oci_path,
                all_params.repo_dir,
                all_params.version_label,
            ],
            steps=[
                clone_repo_step,
                build_base_image_step,
            ],
            volumes=volumes,
        ),
    )


def notify_task(
    env_vars,
    volumes,
    volume_mounts,
):
    params = [
        all_params.additional_recipients,
        all_params.cicd_cfg_name,
        all_params.committish,
        all_params.disable_notifications,
        all_params.giturl,
        all_params.only_recipients,
        all_params.repo_dir,
        all_params.status_dict_str,
        all_params.namespace,
        all_params.pipeline_name,
        all_params.pipeline_run_name,
        all_params.architecture,
        all_params.gardenlinux_epoch,
        all_params.modifiers,
        all_params.platform,
        all_params.publishing_actions,
        all_params.version,
    ]
    clone_step =  steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    log_step = steps.get_logs_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    attach_log_step = steps.attach_log_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    notify_step = steps.notify_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name='notify-task'),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_step,
                attach_log_step,
                log_step,
                notify_step,
            ],
            volumes=volumes,
        ),
    )
    return task
