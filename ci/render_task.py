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

def multiline_str_presenter(dumper, data):
    try:
        dlen = len(data.splitlines())
        if (dlen > 1):
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    except TypeError as ex:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--use-secrets-server', action='store_true')
    parser.add_argument('--outfile', default='tasks.yaml')
    parser.add_argument('--giturl', default='https://github.com/gardenlinux/gardenlinux')
    parser.add_argument('--minimal', action='store_true',  help='omit prebuild and promote steps')

    parsed = parser.parse_args()

    if not parsed.use_secrets_server:
        env_vars = [{
            'name': 'SECRETS_SERVER_CACHE',
            'value': '/secrets/config.json',
        }]
        volume_mounts = [{
            'name': 'secrets',
            'mountPath': '/secrets',
        }]
    else:
        env_vars = []
        volume_mounts = []

    base_build_task_yaml_path = os.path.join(paths.own_dir, 'baseimage_build_task.yaml.template')
    with open(base_build_task_yaml_path) as f:
        raw_base_build_task = yaml.safe_load(f)
    
    build_task_yaml_path = os.path.join(paths.own_dir, 'build-task.yaml.template')
    with open(build_task_yaml_path) as f:
        raw_build_task = yaml.safe_load(f)

    promote_task = tasks.promote_task(
        branch=NamedParam(name='branch'),
        cicd_cfg_name=NamedParam(name='cicd_cfg_name'),
        committish=NamedParam(name='committish'),
        flavourset=NamedParam(name='flavourset'),
        gardenlinux_epoch=NamedParam(name='gardenlinux_epoch'),
        publishing_actions=NamedParam(name='publishing_actions'),
        snapshot_timestamp=NamedParam(name='snapshot_timestamp'),
        version=NamedParam(name='version'),
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    raw_promote_task = dataclasses.asdict(promote_task)

    clone_step = steps.clone_step(
        committish=NamedParam(name='committish'),
        git_url=NamedParam(name='giturl'),
        repo_dir=NamedParam(name='repodir'),
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    clone_step_dict = dataclasses.asdict(clone_step)

    pre_build_step = steps.pre_build_step(
        architecture=NamedParam(name='architecture'),
        cicd_cfg_name=NamedParam(name='cicd_cfg_name'),
        committish=NamedParam(name='committish'),
        gardenlinux_epoch=NamedParam(name='gardenlinux_epoch'),
        modifiers=NamedParam(name='modifiers'),
        platform=NamedParam(name='platform'),
        publishing_actions=NamedParam(name='publishing_actions'),
        repo_dir=NamedParam(name='repodir'),
        version=NamedParam(name='version'),
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    pre_build_step_dict = dataclasses.asdict(pre_build_step)

    upload_step = steps.upload_results_step(
        architecture=NamedParam(name='architecture'),
        cicd_cfg_name=NamedParam(name='cicd_cfg_name'),
        committish=NamedParam(name='committish'),
        gardenlinux_epoch=NamedParam(name='gardenlinux_epoch'),
        modifiers=NamedParam(name='modifiers'),
        outfile=NamedParam(name='outfile'),
        platform=NamedParam(name='platform'),
        publishing_actions=NamedParam(name='publishing_actions'),
        repo_dir=NamedParam(name='repodir'),
        version=NamedParam(name='version'),
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    upload_step_dict = dataclasses.asdict(upload_step)

    promote_step = steps.promote_single_step(
        architecture=NamedParam(name='architecture'),
        cicd_cfg_name=NamedParam(name='cicd_cfg_name'),
        committish=NamedParam(name='committish'),
        gardenlinux_epoch=NamedParam(name='gardenlinux_epoch'),
        modifiers=NamedParam(name='modifiers'),
        platform=NamedParam(name='platform'),
        publishing_actions=NamedParam(name='publishing_actions'),
        repo_dir=NamedParam(name='repodir'),
        version=NamedParam(name='version'),
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )

    promote_step_dict = dataclasses.asdict(promote_step)

    # hack: patch-in clone-step (avoid redundancy with other tasks)
    raw_build_task['spec']['steps'][0] = clone_step_dict
    raw_build_task['spec']['steps'][1] = pre_build_step_dict
    raw_build_task['spec']['steps'][-1] = upload_step_dict

    raw_build_task['spec']['steps'].append(promote_step_dict)
    if not parsed.use_secrets_server:
        print(raw_build_task['spec']['volumes'])
        raw_build_task['spec']['volumes'].append({
            'name': 'secrets',
            'secret': {
                'secretname': 'secrets',
            }
        })

    # Take the template and dynamically set steps for build-base-image
    raw_base_build_task['spec']['steps'][0] = clone_step_dict
    if not parsed.use_secrets_server:
        print(raw_base_build_task['spec']['volumes'])
        raw_base_build_task['spec']['volumes'].append({
            'name': 'secrets',
            'secret': {
                'secretname': 'secrets',
            }
        })

    # Set a custom string representer so that script tags are rendered as 
    # | block style 
    # This should do the trick but add_representer has noeffect on safe dumper
    # yaml.add_representer(str, multiline_str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, multiline_str_presenter)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump_all((raw_base_build_task, raw_build_task, raw_promote_task), f)

    print(f'dumped tasks to {parsed.outfile}')


if __name__ == '__main__':
    main()
