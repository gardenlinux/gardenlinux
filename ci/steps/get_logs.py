#!/usr/bin/env python3
#  export KUBECONFIG=/Users/d058463/Documents/SAP-Dev/Kubernetes/kubeconfigs/kubeconfig--gdnlinux--build.yaml
from collections import namedtuple
from dataclasses import dataclass
import os
from typing import Dict
import zipfile

from kubernetes import client, config


def getlogs(repo_dir: str, namespace: str, pipeline_run_name: str):
    @dataclass
    class TaskRunInfo:
        name: str
        pod_name: str
        steps: Dict[str, str]  # step-name --> step container

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
    zip_name = os.path.join(repo_dir, 'build_log.zip')
    with zipfile.ZipFile(zip_name, mode='w') as log_zip:
        for run_info in task_run_infos:
            pod_name = run_info.pod_name
            counter = 0
            for step, container_name in run_info.steps.items():
                zip_comp = f'{run_info.name}/{counter:02}_{step}.log'
                print(f'Getting logs for pod {pod_name}, step {step} in container {container_name}')
                # Note the flag preload_content decides about streaming or full content in response,
                # k8s client uses internally urllib3, see
                # https://urllib3.readthedocs.io/en/stable/advanced-usage.html#stream
                log_response = k8s.read_namespaced_pod_log_with_http_info(
                    name=pod_name,
                    container=container_name,
                    namespace=namespace,
                    _preload_content=False,
                )
                # returns tuple (response_data, http status, headers)
                K8sResponse = namedtuple("K8sResponse", ["data", "status", "header"])
                log_response = K8sResponse(*log_response)
                if log_response.status != 200:
                    print(f'Getting logs failed with http-error {log_response.status}')
                else:
                    chunk_size = 64 * 1024
                    with log_zip.open(zip_comp, mode='w') as zipcomp:
                        end_reached = False
                        while not end_reached:
                            chunk = log_response.data.read(chunk_size)
                            if len(chunk) > 0:
                                zipcomp.write(chunk)
                            else:
                                end_reached = True
                counter += 1
