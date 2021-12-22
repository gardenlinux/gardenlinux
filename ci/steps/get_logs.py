#!/usr/bin/env python3
import logs


def getlogs(
    repo_dir: str,
    namespace: str,
    pipeline_run_name: str,
    zip_file_path:str=None,
    tail_lines:int=None,
    only_failed:bool=True,
) -> str:
    logs.load_kube_config()
    pipeline_run = logs.get_pipeline_run(pipeline_run_name, namespace)

    return logs.get_and_zip_logs(
        pipeline_run=pipeline_run,
        repo_dir=repo_dir,
        namespace=namespace,
        pipeline_run_name=pipeline_run_name,
        zip_file_path=zip_file_path,
        tail_lines=tail_lines,
        only_failed=only_failed,
    )
