#!/usr/bin/env python3

import argparse
import dataclasses
import os

import yaml

import steps
import tasks
import tkn.model
import paths


NamedParam = tkn.model.NamedParam


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', default='tasks.yaml')

    parsed = parser.parse_args()

    build_task_yaml_path = os.path.join(paths.own_dir, 'build-task.yaml.template')
    with open(build_task_yaml_path) as f:
        raw_build_task = yaml.safe_load(f)

    promote_task = tasks.promote_task(
        branch=NamedParam(name='branch'),
        committish=NamedParam(name='committish'),
        gardenlinux_epoch=NamedParam(name='gardenlinux_epoch'),
        snapshot_timestamp=NamedParam(name='snapshot_timestamp'),
        cicd_cfg_name=NamedParam(name='cicd_cfg_name'),
        version=NamedParam(name='version'),
        promote_target=NamedParam(name='promote_target'),
        promote_mode=NamedParam(name='promote_mode'),
        flavourset=NamedParam(name='flavourset'),
    )

    raw_promote_task = dataclasses.asdict(promote_task)


    clone_step = steps.clone_step(
        committish=tkn.model.NamedParam(name='committish'),
        repo_dir=tkn.model.NamedParam(name='repodir'),
        git_url=tkn.model.NamedParam(name='giturl'),
    )

    clone_step_dict = dataclasses.asdict(clone_step)

    pre_build_step = steps.pre_build_step(
        cicd_cfg_name=NamedParam(name='cicd_cfg_name'),
        committish=tkn.model.NamedParam(name='committish'),
        version=NamedParam(name='version'),
        gardenlinux_epoch=NamedParam(name='gardenlinux_epoch'),
        modifiers=NamedParam(name='modifiers'),
        architecture=NamedParam(name='architecture'),
        platform=NamedParam(name='platform'),
        repo_dir=tkn.model.NamedParam(name='repodir'),
    )

    pre_build_step_dict = dataclasses.asdict(pre_build_step)

    upload_step = steps.upload_results_step(
        cicd_cfg_name=NamedParam(name='cicd_cfg_name'),
        committish=NamedParam(name='committish'),
        architecture=NamedParam(name='architecture'),
        platform=NamedParam(name='platform'),
        gardenlinux_epoch=NamedParam(name='gardenlinux_epoch'),
        modifiers=NamedParam(name='modifiers'),
        version=NamedParam(name='version'),
        outfile=NamedParam(name='outfile'),
        repo_dir=tkn.model.NamedParam(name='repodir'),
    )

    upload_step_dict = dataclasses.asdict(upload_step)

    # hack: patch-in clone-step (avoid redundancy with other tasks)
    raw_build_task['spec']['steps'][0] = clone_step_dict
    raw_build_task['spec']['steps'][1] = pre_build_step_dict
    raw_build_task['spec']['steps'][-1] = upload_step_dict

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump_all((raw_build_task, raw_promote_task), f)

    print(f'dumped tasks to {parsed.outfile}')


if __name__ == '__main__':
    main()
