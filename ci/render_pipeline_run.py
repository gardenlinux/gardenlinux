#!/usr/bin/env python3

import argparse
import dataclasses
import yaml

import glci.model
import glci.util
import tkn.model
import paths

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
    flavour_set: glci.model.GardenlinuxFlavourSet,
):
    run_name = f'{pipeline_name}-{committish}'[:60] # k8s length restriction

    snapshot_timestamp = glci.model.snapshot_date(gardenlinux_epoch=gardenlinux_epoch)

    def mk_workspace(idx: int):
        # XXX hard-coded naming convention
        workspace = PipelineRunWorkspace(
                name=f'ws-{idx}',
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
        )
        return workspace

    flavour_count = len(list(flavour_set.flavours()))
    if flavour_count == 0:
        flavour_count = 1 # at least one workspace must be created

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
                mk_workspace(idx) for idx in range(flavour_count)
            ]
        ),
    )
    return plrun


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--committish', default='master')
    parser.add_argument('--gardenlinux-epoch', default=glci.model.gardenlinux_epoch())
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--pipeline-cfg', default=paths.flavour_cfg_path)
    parser.add_argument('--outfile', default='pipeline_run.yaml')
    parser.add_argument('--flavour-set', default='all')

    parsed = parser.parse_args()

    flavour_set = glci.util.flavour_set(
        flavour_set_name=parsed.flavour_set,
        build_yaml=parsed.pipeline_cfg,
    )


    # XXX hardcode pipeline names and flavour for now
    pipeline_run = mk_pipeline_run(
        pipeline_name='build-gardenlinux-snapshot-pipeline',
        namespace='gardenlinux-tkn',
        committish=parsed.committish,
        gardenlinux_epoch=parsed.gardenlinux_epoch,
        cicd_cfg=parsed.cicd_cfg,
        flavour_set=flavour_set,
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()
