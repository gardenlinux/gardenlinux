import enum
import os
import typing

import glci.model
import tkn.model

DEFAULT_IMAGE = 'eu.gcr.io/gardener-project/cc/job-image:1.640.0'

own_dir = os.path.abspath(os.path.dirname(__file__))
scripts_dir = os.path.join(own_dir)


class ScriptType(enum.Enum):
    BOURNE_SHELL = 'sh'
    PYTHON3 = 'python3'


def task_step_script(
    path: str,
    script_type: ScriptType,
    callable: str,
    params: typing.List[tkn.model.NamedParam],
):
    '''
    renders an inline-step-script, prepending a shebang, and appending an invocation
    of the specified callable (passing the given params).
    '''
    with open(path) as f:
        script = f.read()

    if script_type is ScriptType.PYTHON3:
        shebang = '#!/usr/bin/env python3'
        args = ','.join((
            f"{param.name.replace('-', '_')}='$(params.{param.name})'" for param in params
        ))
        callable_str = f'{callable}({args})'
    elif script_type is ScriptType.BOURNE_SHELL:
        shebang = '#!/usr/bin/env sh'
        args = ' '.join(param.name for param in params)
        callable_str = 'f{callable} {args}'


    return '\n'.join((
        shebang,
        script,
        callable_str,
    ))


def clone_step(
    committish: tkn.model.NamedParam,
    repo_dir: tkn.model.NamedParam,
    git_url: tkn.model.NamedParam,
):
    step = tkn.model.TaskStep(
        name='clone-repo-step',
        image='eu.gcr.io/gardener-project/cc/job-image:1.640.0',
        script=task_step_script(
            path=os.path.join(scripts_dir, 'clone_repo_step.py'),
            script_type=ScriptType.PYTHON3,
            callable='clone_and_copy',
            params=[
                committish,
                repo_dir,
                git_url,
            ],
        ),
    )

    return step
