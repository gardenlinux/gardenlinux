import enum
import os
import typing

import tkn.model

DEFAULT_IMAGE = 'eu.gcr.io/gardener-project/cc/job-image:1.640.0'

own_dir = os.path.abspath(os.path.dirname(__file__))
scripts_dir = os.path.join(own_dir)


def extend_python_path_snippet(param_name: str):
    sd_name = os.path.basename(scripts_dir)
    return f'sys.path.insert(1,os.path.abspath(os.path.join("$(params.{param_name})","{sd_name}")))'


class ScriptType(enum.Enum):
    BOURNE_SHELL = 'sh'
    PYTHON3 = 'python3'


def task_step_script(
    path: str,
    script_type: ScriptType,
    callable: str,
    params: typing.List[tkn.model.NamedParam],
    repo_path_param: typing.Optional[tkn.model.NamedParam]=None,
):
    '''
    renders an inline-step-script, prepending a shebang, and appending an invocation
    of the specified callable (passing the given params).
    '''
    with open(path) as f:
        script = f.read()

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
        shebang = '#!/usr/bin/env sh'
        preamble = ''
        args = ' '.join(param.name for param in params)
        callable_str = 'f{callable} {args}'


    return '\n'.join((
        shebang,
        preamble,
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
            repo_path_param=repo_dir,
        ),
    )

    return step


def build_image_step(
    suite: tkn.model.NamedParam,
    gardenlinux_epoch: tkn.model.NamedParam,
    snapshot_timestamp: tkn.model.NamedParam,
    platform: tkn.model.NamedParam,
    modifiers: tkn.model.NamedParam,
    outfile: tkn.model.NamedParam,
    repodir: tkn.model.NamedParam,
):
    pass
