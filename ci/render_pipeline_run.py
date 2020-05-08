#!/usr/bin/env python3

import argparse
import dataclasses
import os
import yaml

import glci.model
import tkn.model

own_dir = os.path.abspath(os.path.dirname(__file__))

GardenlinuxFlavour = glci.model.GardenlinuxFlavour

PipelineRef = tkn.model.PipelineRef
PipelineRun = tkn.model.PipelineRun
PipelineRunSpec = tkn.model.PipelineRunSpec
PipelineRunMetadata = tkn.model.PipelineRunMetadata
PipelineMetadata = tkn.model.PipelineMetadata
PodTemplate = tkn.model.PodTemplate
TaskRef = tkn.model.TaskRef
PipelineTask = tkn.model.PipelineTask
NamedParam = tkn.model.NamedParam


def mk_pipeline_run(
    pipeline_name: str,
    namespace: str,
    committish: str,
    aws_cfg: str,
    s3_bucket: str,
):
    run_name = f'{pipeline_name}-{committish}'[:60] # k8s length restriction

    plrun = PipelineRun(
        metadata=PipelineRunMetadata(
            name=run_name,
            namespace=namespace,
        ),
        spec=PipelineRunSpec(
            params=[
                NamedParam(
                    name='committish',
                    value=committish,
                ),
                NamedParam(
                    name='aws_cfg_name',
                    value=aws_cfg,
                ),
                NamedParam(
                    name='s3_bucket_name',
                    value=s3_bucket,
                ),
            ],
            pipelineRef=PipelineRef(
                name=pipeline_name,
            ),
            podTemplate=PodTemplate(
                nodeSelector={
                    "worker.garden.sapcloud.io/group": "gl-build"
                }
            )
        ),
    )
    return plrun


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--committish', default='master')
    parser.add_argument('--aws-cfg', default='gardenlinux-dev')
    parser.add_argument('--s3-bucket', default='gardenlinux-test')
    parser.add_argument('--outfile', default='pipeline_run.yaml')

    parsed = parser.parse_args()

    # XXX hardcode pipeline names and flavour for now
    pipeline_run = mk_pipeline_run(
        pipeline_name='build-gardenlinux-snapshot-pipeline',
        namespace='gardenlinux-tkn',
        committish=parsed.committish,
        aws_cfg=parsed.aws_cfg,
        s3_bucket=parsed.s3_bucket,
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()
