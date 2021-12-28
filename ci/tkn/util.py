import collections
import dataclasses
import enum
import json
import logging
import shutil
import subprocess
import time

import dacite
import dateutil.parser

logger = logging.getLogger(__name__)


def _tkn_executable():
    if not (tkn := shutil.which('tkn')):
        raise ValueError('did not find `tkn` in PATH')
    return tkn


class StatusReason(enum.Enum):
    RUNNING = 'Running'
    FAILED = 'Failed'
    SUCCEEDED = 'Succeeded'
    PIPELINE_RUN_STOPPING = 'PipelineRunStopping'
    PIPELINE_RUN_CANCELLED = 'PipelineRunCancelled'
    TASK_RUN_CANCELLED = 'TaskRunCancelled'
    EXCEEDED_NODE_RESOURCES = 'ExceededNodeResources'


@dataclasses.dataclass
class TknCondition:
    lastTransitionTime: str
    message: str
    reason: StatusReason
    status: str # either True|False, or Unknown
    type: str


def run_tkn(*args, namespace: str='gardenlinux'):
    tkn = _tkn_executable()
    logger.debug(args)

    result = subprocess.run(
        [
            tkn,
            '--namespace', namespace,
            *args,
            '-o', 'json',
        ],
        capture_output=True,
        text=True,
    )

    return result


def _pipelinerun(name: str, namespace: str='gardenlinux'):
    res = run_tkn(
        'pipelinerun',
        'describe',
        name,
        namespace=namespace,
    )

    if not res.returncode == 0:
        logger.debug(res.stdout)
        logger.debug(res.stderr)
        raise RuntimeError(f'pipelinerun cmd returned {res.returncode}')

    res_dict = json.loads(res.stdout)
    return res_dict


def _run_status(dict_with_status: dict):
    '''
    determines the current status of a given tekton entity bearing a `status`.
    Examples of such entities are:
    - pipelineruns
    - taskruns

    the passed `dict` is expected to bear an attribute `status`, with a sub-attr `conditions`, which
    in turn is parsable into a list of `TknCondition`
    '''
    if not 'status' in dict_with_status:
        # XXX if we are too early, there is no status, yet
        return None

    status = dict_with_status['status']
    conditions = [
        dacite.from_dict(
            data=condition,
            data_class=TknCondition,
            config=dacite.Config(
                cast=[
                    StatusReason,
                ],
            ),
        ) for condition in status['conditions']
    ]

    latest_condition = sorted(
        conditions,
        key=lambda c: dateutil.parser.isoparse(c.lastTransitionTime)
    )[-1]

    return latest_condition


def pipelinerun_status(name: str, namespace: str='gardenlinux'):
    pipelinerun_dict = _pipelinerun(name=name, namespace=namespace)

    return _run_status(dict_with_status=pipelinerun_dict)


def wait_for_pipelinerun_status(
    name: str,
    namespace: str='gardenlinux',
    target_status: StatusReason=StatusReason.SUCCEEDED,
    timeout_seconds: int=60*45, # 45 minutes
    polling_interval_seconds: int=15,
):
    start_time = time.time()

    while (status := pipelinerun_status(name=name, namespace=namespace)) or True:
        if not status is None:
            reason = status.reason
            if reason is target_status:
                print(f'{target_status=} reached - build finished')
                break
        else:
            reason = None

        logger.debug(f'{reason=}')
        if reason in (StatusReason.FAILED, StatusReason.PIPELINE_RUN_CANCELLED):
            logger.error(f'{reason=} - aborting')
            raise RuntimeError(reason)
        elif reason in (StatusReason.RUNNING, StatusReason.PIPELINE_RUN_STOPPING, None):
            passed_seconds = time.time() - start_time
            if passed_seconds > timeout_seconds:
                raise RuntimeError(f'timeout exceeded: {timeout_seconds=}')
            time.sleep(polling_interval_seconds)
        else:
            raise NotImplementedError(reason)

    logger.info(f'pipelinerun {name=} reached {target_status=}')


def pipeline_taskrun_status(name: str, namespace: str='gardenlinux'):
    pipelinerun_dict = _pipelinerun(name=name, namespace=namespace)
    status = pipelinerun_dict['status']
    taskruns = status['taskRuns'] # {<taskrun-id>: <taskrun-status>}

    succeeded_taskrun_names = []
    pending_taskrun_names = []
    failed_taskruns = []

    for tr_id, tr_dict in taskruns.items():
        status = _run_status(dict_with_status=tr_dict)
        tr_name = tr_dict['pipelineTaskName']

        if status.status.lower() == 'true':
            succeeded_taskrun_names.append(tr_name)
        elif status.status.lower() == 'unknown':
            pending_taskrun_names.append(tr_name)
        else:
            failed_taskruns.append({
                'name': tr_name,
                'message': status.message,
            })

    TaskStatusSummary = collections.namedtuple(
        'TaskStatusSummary',
        ['succeeded_names', 'pending_names', 'failed_details']
    )

    return TaskStatusSummary(
        succeeded_names=succeeded_taskrun_names,
        pending_names=pending_taskrun_names,
        failed_details=failed_taskruns,
    )
