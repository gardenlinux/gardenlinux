#!/usr/bin/env python3

import argparse
import dataclasses
import os

import yaml

import tasks
import tkn.model


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

    if secret_key := os.getenv('SECRET_KEY'):
        env_vars.append({
            'name': 'SECRET_KEY',
            'value': secret_key,
        })
    if concourse_current_team := os.getenv('CONCOURSE_CURRENT_TEAM'):
        env_vars.append({
            'name': 'CONCOURSE_CURRENT_TEAM',
            'value': concourse_current_team,
        })
    if secret_server_concourse_cfg_name := os.getenv('SECRETS_SERVER_CONCOURSE_CFG_NAME'):
        env_vars.append({
            'name': 'SECRETS_SERVER_CONCOURSE_CFG_NAME',
            'value': secret_server_concourse_cfg_name,
        })
    if secret_cipher_algorithm := os.getenv('SECRET_CIPHER_ALGORITHM'):
        env_vars.append({
            'name': 'SECRET_CIPHER_ALGORITHM',
            'value': secret_cipher_algorithm,
        })

    base_build_task = tasks.base_image_build_task(
        volume_mounts=volume_mounts,
        env_vars=env_vars,
    )
    raw_base_build_task = dataclasses.asdict(base_build_task)

    package_task = tasks.nokernel_package_task(
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    raw_package_task = dataclasses.asdict(package_task)

    kernel_package_task = tasks.kernel_package_task(
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    raw_kernel_package_task = dataclasses.asdict(kernel_package_task)

    build_task = tasks.build_task(
        env_vars=env_vars,
        volume_mounts=volume_mounts,
    )
    raw_build_task = dataclasses.asdict(build_task)

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

    # Set a custom string representer so that script tags are rendered as
    # | block style
    # This should do the trick but add_representer has noeffect on safe dumper
    # yaml.add_representer(str, multiline_str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, multiline_str_presenter)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump_all(
            (
                raw_base_build_task,
                raw_build_task,
                raw_kernel_package_task,
                raw_package_task,
                raw_promote_task,
            ),
            f,
        )

    print(f'dumped tasks to {parsed.outfile}')


if __name__ == '__main__':
    main()
