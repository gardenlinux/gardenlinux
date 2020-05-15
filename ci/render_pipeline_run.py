#!/usr/bin/env python3

import argparse
import dataclasses
import yaml

import glci.model
import tkn.model

GardenlinuxFlavour = glci.model.GardenlinuxFlavour

NamedParam = tkn.model.NamedParam
PipelineMetadata = tkn.model.PipelineMetadata
PipelineRef = tkn.model.PipelineRef
PipelineRun = tkn.model.PipelineRun
PipelineRunMetadata = tkn.model.PipelineRunMetadata
PipelineRunSpec = tkn.model.PipelineRunSpec
PipelineRunWorkspace = tkn.model.PipelineRunWorkspace
PipelineTask = tkn.model.PipelineTask
PodTemplate = tkn.model.PodTemplate
ResourcesClaim = tkn.model.ResourcesClaim
ResourcesClaimRequests = tkn.model.ResourcesClaimRequests
TaskRef = tkn.model.TaskRef
VolumeClaimTemplate = tkn.model.VolumeClaimTemplate
VolumeClaimTemplateSpec = tkn.model.VolumeClaimTemplateSpec


def mk_pipeline_run(
    pipeline_name: str,
    namespace: str,
    committish: str,
    gardenlinux_epoch: int,
    cicd_cfg: str,
):
    run_name = f'{pipeline_name}-{committish}'[:60] # k8s length restriction

    snapshot_timestamp = glci.model.snapshot_date(gardenlinux_epoch=gardenlinux_epoch)

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
                    name='gardenlinux_epoch',
                    value=str(gardenlinux_epoch), # tekton only knows str
                ),
                NamedParam(
                    name='snapshot_timestamp',
                    value=snapshot_timestamp,
                ),
                NamedParam(
                    name='cicd_cfg_name',
                    value=cicd_cfg,
                ),
            ],
            pipelineRef=PipelineRef(
                name=pipeline_name,
            ),
            podTemplate=PodTemplate(
                nodeSelector={
                    "worker.garden.sapcloud.io/group": "gl-build"
                }
            ),
            workspaces=[
                PipelineRunWorkspace(
                    name='ws',
                    volumeClaimTemplate=VolumeClaimTemplate(
                        spec=VolumeClaimTemplateSpec(
                            accessModes=['ReadWriteOnce'],
                            resources=ResourcesClaim(
                                requests=ResourcesClaimRequests(
                                    storage='128Mi',
                                ),
                            ),
                        ),
                    ),
                ),
            ]
        ),
    )
    return plrun


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--committish', default='master')
    parser.add_argument('--gardenlinux-epoch', default=glci.model.gardenlinux_epoch())
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--outfile', default='pipeline_run.yaml')

    parsed = parser.parse_args()

    # XXX hardcode pipeline names and flavour for now
    pipeline_run = mk_pipeline_run(
        pipeline_name='build-gardenlinux-snapshot-pipeline',
        namespace='gardenlinux-tkn',
        committish=parsed.committish,
        gardenlinux_epoch=parsed.gardenlinux_epoch,
        cicd_cfg=parsed.cicd_cfg,
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()
