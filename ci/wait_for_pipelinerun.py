#!/usr/bin/env python3

import argparse

import yaml

import tkn.util


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pipelinerun-name')
    parser.add_argument('--pipelinerun-file')
    parser.add_argument('--namespace', default='gardenlinux-tkn')

    parsed = parser.parse_args()

    pipelinerun_name = parsed.pipelinerun_name
    pipelinerun_file = parsed.pipelinerun_file
    namespace = parsed.namespace

    if not bool(pipelinerun_file) ^ bool(pipelinerun_name):
        raise ValueError('exactly ony of pipelinerun-name or -file must be given')

    if pipelinerun_file:
        with open(pipelinerun_file) as f:
            parsed_pipelinerun = yaml.safe_load(f)
            metadata = parsed_pipelinerun['metadata']
            pipelinerun_name = metadata['name']
            namespace = metadata['namespace']

    print(f'waiting for {pipelinerun_name=} to finish')

    try:
        tkn.util.wait_for_pipelinerun_status(
            name=pipelinerun_name,
            namespace=namespace,
        )
        print('{pipelinerun=} succeeded')

    except RuntimeError as rte:
        print(rte)
        print('pipeline run failed')


if __name__ == '__main__':
    main()
