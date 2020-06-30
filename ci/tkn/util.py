import dataclasses
import enum
import json
import shutil
import subprocess
import time

import dacite
import dateutil.parser


def _tkn_executable():
    if not (tkn := shutil.which('tkn')):
        raise ValueError('did not find `tkn` in PATH')
    return tkn


class StatusReason(enum.Enum):
    RUNNING = 'Running'
    FAILED = 'Failed'
    SUCCEEDED = 'Succeeded'


@dataclasses.dataclass
class TknCondition:
    lastTransitionTime: str
    message: str
    reason: StatusReason
    status: str
    type: str


def run_tkn(*args, namespace: str='gardenlinux-tkn'):
    tkn = _tkn_executable()
    print(args)

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


def _pipelinerun(name: str, namespace: str='gardenlinux-tkn'):
    res = run_tkn(
        'pipelinerun',
        'describe',
        name,
        namespace=namespace,
    )

    if not res.returncode == 0:
        print(res.stdout)
        print(res.stderr)
        raise RuntimeError(f'pipelinerun cmd returned {res.returncode}')

    res_dict = json.loads(res.stdout)
    return res_dict


def pipelinerun_status(name: str, namespace: str='gardenlinux-tkn'):
    pipelinerun_dict = _pipelinerun(name=name, namespace=namespace)
    status = pipelinerun_dict['status']
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


def wait_for_pipelinerun_status(
    name: str,
    namespace: str='gardenlinux-tkn',
    target_status: StatusReason=StatusReason.SUCCEEDED,
    timeout_seconds: int=60*30, # 30 minutes
    polling_interval_seconds: int=15,
):
    start_time = time.time()

    while (status := pipelinerun_status(name=name, namespace=namespace).reason) is not target_status:
        if status is StatusReason.FAILED:
            print(f'{status=} - aborting')
            raise RuntimeError(status)
        elif status is StatusReason.RUNNING:
            passed_seconds = time.time() - start_time
            if passed_seconds > timeout_seconds:
                raise RuntimeError(f'timeout exceeded: {timeout_seconds=}')
            time.sleep(polling_interval_seconds)
        else:
            raise NotImplementedError(status)

    print(f'pipelinerun {name=} reached {target_status=}')
