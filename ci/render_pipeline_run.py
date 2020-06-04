#!/usr/bin/env python3

import argparse
import dataclasses
import yaml

import glci.model
import glci.util
import tkn.model
import paths
import promote

GardenlinuxFlavour = glci.model.GardenlinuxFlavour

NamedParam = tkn.model.NamedParam
PipelineRef = tkn.model.PipelineRef
PipelineRun = tkn.model.PipelineRun
PipelineRunMetadata = tkn.model.PipelineRunMetadata
PipelineRunSpec = tkn.model.PipelineRunSpec
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
    version: str,
    flavour_set: glci.model.GardenlinuxFlavourSet,
    promote_target: promote.BuildType,
    promote_mode: promote.PromoteMode,
):
    run_name = f'{pipeline_name}-{version.replace(".", "-")}'[:60] # k8s length restriction

    snapshot_timestamp = glci.model.snapshot_date(gardenlinux_epoch=gardenlinux_epoch)

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
                NamedParam(
                    name='version',
                    value=version,
                ),
                NamedParam(
                    name='flavourset',
                    value=flavour_set.name,
                ),
                NamedParam(
                    name='promote_target',
                    value=promote_target.value,
                ),
                NamedParam(
                    name='promote_mode',
                    value=promote_mode.value,
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
            workspaces=[],
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
    parser.add_argument('--version', default=None)
    parser.add_argument(
        '--promote-target',
        type=promote.BuildType,
        default=promote.BuildType.SNAPSHOT,
    )
    parser.add_argument(
        '--promote-mode',
        type=promote.PromoteMode,
        default=promote.PromoteMode.MANIFESTS_ONLY,
    )

    parsed = parser.parse_args()

    flavour_set = glci.util.flavour_set(
        flavour_set_name=parsed.flavour_set,
        build_yaml=parsed.pipeline_cfg,
    )

    if (version:=parsed.version) is None:
        version = f'{parsed.gardenlinux_epoch}-{parsed.committish[:6]}'


    # XXX hardcode pipeline names and flavour for now
    pipeline_run = mk_pipeline_run(
        pipeline_name='gardenlinux-build',
        namespace='gardenlinux-tkn',
        committish=parsed.committish,
        gardenlinux_epoch=parsed.gardenlinux_epoch,
        cicd_cfg=parsed.cicd_cfg,
        flavour_set=flavour_set,
        version=version,
        promote_target=parsed.promote_target,
        promote_mode=parsed.promote_mode,
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()
