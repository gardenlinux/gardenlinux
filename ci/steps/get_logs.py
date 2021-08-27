#!/usr/bin/env python3
from dataclasses import dataclass
import os
import urllib3
from typing import Dict
import zipfile

from kubernetes import client, config


@dataclass
class TaskRunInfo:
    name: str
    pod_name: str
    steps: Dict[str, str]  # step-name --> step container


@dataclass
class K8sResponse:
    data: urllib3.response.HTTPResponse
    status_code: int # http-status-code
    headers: urllib3.response.HTTPHeaderDict


def _get_and_zip_logs(
    repo_dir: str,
    namespace: str,
    pipeline_run_name: str,
    zip_file_path:str,
    tail_lines,
) -> str:
    '''
    retrieves all pod logs and writes them into a zip archive

    tail_lines: limits the amount of lines returned from each pod log
    '''

    config.load_incluster_config()
    # in case you want to run locally use:
    # config.load_kube_config()

    k8s = client.CoreV1Api()
    # fetching the custom resource definition (CRD) api
    api = client.CustomObjectsApi()
    pipeline_run = api.get_namespaced_custom_object(
        group="tekton.dev",
        namespace=namespace,
        name=pipeline_run_name,
        plural='pipelineruns',
        version='v1alpha1',
    )
    # Compile all task names from the PipelineRun
    task_names = [t['name'] for t in pipeline_run['status']['pipelineSpec']['tasks']]
    if 'finally' in  pipeline_run['status']['pipelineSpec']:
        task_names += [t['name'] for t in pipeline_run['status']['pipelineSpec']['finally']]
    print(f'Getting all steps for the followings tasks: {task_names=}')

    # Compile a dictionary with task name as key and pod name as value
    # Note: Dict contains only those tasks that have run and are completed
    task_runs = pipeline_run['status']['taskRuns']
    # pod_dict = {tr['pipelineTaskName']: tr['status']['podName'] for tr in task_runs.values()}

    task_run_infos = []
    for tr in task_runs.values():
        task_steps = {step['name']: step['container'] for step in tr['status']['steps']}
        task_run_infos.append(
            TaskRunInfo(
                name=tr['pipelineTaskName'],
                pod_name=tr['status']['podName'],
                steps=task_steps,
            )
        )

    # create a zip file to store logs:
    if not zip_file_path:
        zip_file_path = os.path.join(repo_dir, 'build_log.zip')

    with zipfile.ZipFile(zip_file_path, mode='w') as log_zip:
        for run_info in task_run_infos:
            pod_name = run_info.pod_name
            # steps: dict {<name>: <container>}
            for idx, (step, container_name) in enumerate(run_info.steps.items()):
                zip_comp = f'{run_info.name}/{idx:02}_{step}.log'
                print(f'Getting logs for pod {pod_name}, step {step} in container {container_name}')
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

                data, status_code, headers = k8s.read_namespaced_pod_log_with_http_info(**args)
                # returns tuple (response_data, http status, headers)
                log_response = K8sResponse(
                    data=data,
                    status_code=status_code,
                    headers=headers,
                )

                if log_response.status_code != 200:
                    print(f'Getting logs failed with {log_response.status_code=}')
                    continue

                with log_zip.open(zip_comp, mode='w') as zipcomp:
                    for chunk in log_response.data.stream(amt=4096):
                        zipcomp.write(chunk)

    return zip_file_path


def getlogs(
    repo_dir: str,
    namespace: str,
    pipeline_run_name: str,
    zip_file_path:str=None,
    tail_lines:int=None,
    status_dict_str:str=None,
) -> str:

    # failed_pods = []
    # if status_dict_str:
    #     status_dict = json.loads(status_dict_str)

    return _get_and_zip_logs(
        repo_dir=repo_dir,
        namespace=namespace,
        pipeline_run_name=pipeline_run_name,
        zip_file_path=zip_file_path,
        tail_lines=tail_lines,
    )
