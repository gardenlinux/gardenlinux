import typing
import params
import results
import steps
import tkn.model

NamedParam = tkn.model.NamedParam

all_params = params.AllParams
all_results = results.AllResults

def unify_params(params: typing.Sequence[NamedParam]) -> typing.Sequence[NamedParam]:
    return list(set(params))


def promote_task(
    name='promote-gardenlinux-task',
    env_vars=[],
    volumes=[],
    volume_mounts=[],
):
    params = [all_params.step_image]
    clone_step, params_step = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    promote_step, params_step = steps.promote_step(
        params=all_params,
        results=all_results,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    release_step, params_step = steps.release_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    build_cd_step, params_step = steps.create_component_descriptor_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step
    params = unify_params(params)

    task = tkn.model.Task(
        metadata=tkn.model.Metadata(name=name),
        spec=tkn.model.TaskSpec(
            params=params,
            results=[results.AllResults.manifest_set_key_result, ],
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


def build_task(
    env_vars,
    volume_mounts,
    volumes=[],
):
    params = [all_params.step_image]

    clone_step, params_step = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    promote_step, params_step = steps.promote_single_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

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

    task_steps = [
        clone_step,
        promote_step,
    ]

    params = unify_params(params)

    return tkn.model.Task(
        metadata=tkn.model.Metadata(name='build-gardenlinux-task'),
        spec=tkn.model.TaskSpec(
            params=params,
            results=[results.AllResults.build_result, ],
            steps=task_steps,
            volumes=task_volumes,
        ),
    )


def test_task(
    env_vars,
    volume_mounts,
    volumes=[],
):
    params = [all_params.step_image]
    clone_step, params_step = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    pre_check_tests_step, params_step = steps.pre_check_tests_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    test_step, params_step = steps.test_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    upload_test_results_step, params_step = steps.upload_test_results_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step
    params = unify_params(params)

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
            params=params,
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
    params = []

    clone_repo_step, params_step = steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    build_step_image_step, params_step = steps.build_step_image_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step
    params = unify_params(params)

    return tkn.model.Task(
        metadata=tkn.model.Metadata(name='build-baseimage'),
        spec=tkn.model.TaskSpec(
            params=params,
            steps=[
                clone_repo_step,
                build_step_image_step,
            ],
            volumes=volumes,
        ),
    )


def notify_task(
    env_vars,
    volumes,
    volume_mounts,
):
    params = [all_params.step_image]
    clone_step, params_step =  steps.clone_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    log_step, params_step = steps.get_logs_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    attach_log_step, params_step = steps.attach_log_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step

    notify_step, params_step = steps.notify_step(
        params=all_params,
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    params += params_step
    params = unify_params(params)

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
