#!/usr/bin/env python3

import argparse
import dataclasses
import os

import yaml

import steps
import tkn.model
import paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--outfile', default='build-task.yaml')

    parsed = parser.parse_args()

    task_yaml_path = os.path.join(paths.own_dir, 'task.yaml')
    with open(task_yaml_path) as f:
        raw_task = yaml.safe_load(f)

    clone_step = steps.clone_step(
        committish=tkn.model.NamedParam(name='committish'),
        repo_dir=tkn.model.NamedParam(name='repodir'),
        git_url=tkn.model.NamedParam(name='giturl'),
    )

    clone_step_dict = dataclasses.asdict(clone_step)

    # hack: patch-in clone-step (avoid redundancy with other tasks)
    raw_task['spec']['steps'][0] = clone_step_dict

    with open(parsed.outfile, 'w') as f:
        yaml.dump(raw_task, f)

    print(f'dumped task to {parsed.outfile}')


if __name__ == '__main__':
    main()
