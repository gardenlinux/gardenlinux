import dataclasses
import logging
import os
import typing
import urllib3
import zipfile

from kubernetes import client, config
from kubernetes.client.rest import ApiException


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class K8sResponse:
    data: urllib3.response.HTTPResponse
    status_code: int # http-status-code
    headers: urllib3.response.HTTPHeaderDict


@dataclasses.dataclass
class TaskRunInfo:
    name: str
    pod_name: str
    steps: typing.Dict[str, str]  # step-name --> step container


def load_kube_config():
    if 'CC_CONFIG_DIR' in os.environ:
        # run locally then use:
        config.load_kube_config()
    else:
        config.load_incluster_config()


def get_pipeline_run(pipeline_run_name: str, namespace: str):
    # fetching the custom resource definition (CRD) api
    api = client.CustomObjectsApi()
    return api.get_namespaced_custom_object(
        group="tekton.dev",
        namespace=namespace,
        name=pipeline_run_name,
        plural='pipelineruns',
        version='v1alpha1',
    )


def  _get_task_run_infos(
    pipeline_run: dict[str, any],
    pipeline_run_name: str,
    only_failed: bool,
):
    # Compile all task names from the PipelineRun
    task_names = [t['name'] for t in pipeline_run['status']['pipelineSpec']['tasks']]
    if 'finally' in  pipeline_run['status']['pipelineSpec']:
        task_names += [t['name'] for t in pipeline_run['status']['pipelineSpec']['finally']]
    logger.info(f'Getting all steps for the followings tasks: {task_names=}')

    # Compile a dictionary with task name as key and pod name as value
    # Note: Dict contains only those tasks that have run and are completed
    task_runs = pipeline_run['status']['taskRuns']
    # pod_dict = {tr['pipelineTaskName']: tr['status']['podName'] for tr in task_runs.values()}

    task_run_infos = []
    for tr in task_runs.values():
        if only_failed:
            # Note that some steps of the pipelineRun are not yet finished. e.g. current step
            # getting the logs and thus do not have a 'terminated' key.
            task_steps = {step['name']: step['container'] for step in tr['status']['steps']
                            if 'terminated' in step and step['terminated']['exitCode'] != 0}
            do_append = tr['status']['conditions'][0]['reason'] != 'Succeeded'
        else:
            task_steps = {step['name']: step['container'] for step in tr['status']['steps']}
            do_append = True

        if do_append:
            task_run_infos.append(
                TaskRunInfo(
                    name=tr['pipelineTaskName'],
                    pod_name=tr['status']['podName'],
                    steps=task_steps,
                )
            )
    return task_run_infos


def get_failed_excerpts(
    namespace: str,
    pipeline_run: dict[str, any],
    pipeline_run_name: str,
    only_failed: bool,
    repo_dir: str,
    lines: int,
):
    task_run_infos = _get_task_run_infos(
        pipeline_run=pipeline_run,
        pipeline_run_name=pipeline_run_name,
        only_failed=only_failed,
    )

    k8s = client.CoreV1Api()
    file_path = os.path.join(repo_dir, 'failed_summary.txt')
    with open(file_path, "w") as out_file:
        for run_info in task_run_infos:
            pod_name = run_info.pod_name
            for idx, (step, container_name) in enumerate(run_info.steps.items()):
                logger.info(
                    f'Getting logs for pod {pod_name}, step {step} in container {container_name}'
                )
                out_file.write(f'### Pod: {pod_name}, step: {step}, container: {container_name}')
                try:
                    data, status_code, headers = k8s.read_namespaced_pod_log_with_http_info(
                        name=pod_name,
                        container=container_name,
                        namespace=namespace,
                        tail_lines=lines,
                    )

                    if status_code >= 400:
                        logger.warning(f'Getting logs failed with {status_code=}')
                        continue

                    out_file.write(data)
                except ApiException as ex:
                    if ex.status == 404:
                        msg = f'Log for pod {pod_name} is already gone {str(ex)}'
                        logger.warning(msg)
                        out_file.write(msg)
                    else:
                        msg = f'Getting logs for pod {pod_name} failed {str(ex)}'
                        logger.error(msg)
                        out_file.write(msg)


def get_and_zip_logs(
    pipeline_run: dict[str, any],
    repo_dir: str,
    namespace: str,
    pipeline_run_name: str,
    zip_file_path:str,
    tail_lines: int,
    only_failed: bool
) -> str:
    '''
    retrieves all pod logs and writes them into a zip archive

    tail_lines: limits the amount of lines returned from each pod log
    '''

    task_run_infos = _get_task_run_infos(
        pipeline_run=pipeline_run,
        pipeline_run_name=pipeline_run_name,
        only_failed=only_failed,
    )

    k8s = client.CoreV1Api()

    # create a zip file to store logs:
    if not zip_file_path:
        zip_file_path = os.path.join(repo_dir, 'build_log.zip')

    with zipfile.ZipFile(zip_file_path, mode='w') as log_zip:
        for run_info in task_run_infos:
            pod_name = run_info.pod_name
            # steps: dict {<name>: <container>}
            for idx, (step, container_name) in enumerate(run_info.steps.items()):
                zip_comp = f'{run_info.name}/{idx:02}_{step}.log'
                logger.info(
                    f'Getting logs for pod {pod_name}, step {step} in container {container_name}'
                )
                # Note the flag preload_content decides about streaming or full content in response,
                # k8s client uses internally urllib3, see
                # https://urllib3.readthedocs.io/en/stable/advanced-usage.html#stream
                # tail lines only if not None:
                args = {
                    'name': pod_name,
                    'container': container_name,
                    'namespace': namespace,
                    '_preload_content': False,
                }
                if tail_lines:
                    args['tail_lines'] = tail_lines

                try:
                    data, status_code, headers = k8s.read_namespaced_pod_log_with_http_info(**args)
                    # returns tuple (response_data, http status, headers)
                    log_response = K8sResponse(
                        data=data,
                        status_code=status_code,
                        headers=headers,
                    )

                    if log_response.status_code >= 400:
                        logger.warning(f'Getting logs failed with {log_response.status_code=}')
                        continue
                except ApiException as ex:
                    if ex.status == 404:
                        logger.warning(f'Log for pod {pod_name} is already gone {str(ex)}')
                    else:
                        logger.error(f'Getting logs for pod {pod_name} failed {str(ex)}')

                    with open(zip_comp, 'w') as f:
                        f.write('Log file for {pod_name} could not be retrieved: {str(ex)}')

                with log_zip.open(zip_comp, mode='w') as zipcomp:
                    for chunk in log_response.data.stream(amt=4096):
                        zipcomp.write(chunk)

    return zip_file_path


def get_task_result(
    task_runs_dict,
    task_ref_name: str,
    result_name: str,
):
    """
    get result value from termination message of a taks run. Read directly the taskRun K8s object
    to find a result from a task. This method avoids using a $(tasks.xyz.results...) construct to
    workaround the problem that using a result requires the task to execute successfully. This
    method allows using a result without having the dependency that the result was actually set.
    """
    task_runs_dict =  task_runs_dict['status']['taskRuns']
    for tr_dict in task_runs_dict.values():
        if tr_dict['pipelineTaskName'] == task_ref_name and 'taskResults' in tr_dict['status']:
            results_dict = tr_dict['status']['taskResults']
            for r in results_dict:
                if r['name'] == result_name:
                    return r['value']
    return None