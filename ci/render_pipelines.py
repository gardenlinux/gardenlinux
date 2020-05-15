#!/usr/bin/env python3

import argparse
import dacite
import dataclasses
import typing

import yaml

import paths
import glci.model
import glci.util
import tkn.model


GardenlinuxFlavour = glci.model.GardenlinuxFlavour

Pipeline = tkn.model.Pipeline
PipelineSpec = tkn.model.PipelineSpec
PipelineMetadata = tkn.model.PipelineMetadata
TaskRef = tkn.model.TaskRef
PipelineTask = tkn.model.PipelineTask
Workspace = tkn.model.Workspace
NamedParam = tkn.model.NamedParam

def pass_param(name: str):
    '''
    create a named-param that will propagate the parent's param value
    '''
    return NamedParam(name=name, value=f'$(params.{name})')


def mk_clone_task(
    gardenlinux_flavour: GardenlinuxFlavour,
    workspace: Workspace,
):
    task_name = gardenlinux_flavour.canonical_name_prefix().replace('/', '-')\
            .replace('_', '-').strip('-')
    return PipelineTask(
        name=f'clone-repo-{task_name}',
        taskRef=TaskRef(name='clone-repo-task'), # hardcode name for now
        workspaces=[workspace],
        params=[
            pass_param(name='committish'),
        ],
    )


def mk_pipeline_task(
    gardenlinux_flavour: GardenlinuxFlavour,
    pipeline_flavour: glci.model.PipelineFlavour,
    workspace: Workspace,
    run_after: typing.List[str],
):
    if not pipeline_flavour is glci.model.PipelineFlavour.SNAPSHOT:
        raise NotImplementedError(pipeline_flavour)

    modifier_names = ','.join(gardenlinux_flavour.modifiers)

    upload_prefix = f'{gardenlinux_flavour.architecture.value}/'

    workspace = dataclasses.replace(workspace, name='gardenlinux-repo')


    task_name = gardenlinux_flavour.canonical_name_prefix().replace('/', '-')\
            .replace('_', '-').strip('-')

    return PipelineTask(
        name=task_name,
        taskRef=TaskRef(name='build-gardenlinux-task'), # hardcode name for now
        workspaces=[workspace],
        params=[
            NamedParam(name='platform', value=gardenlinux_flavour.platform),
            NamedParam(name='modifiers', value=modifier_names),
            NamedParam(name='uploadprefix', value=upload_prefix),
            NamedParam(name='fnameprefix', value=gardenlinux_flavour.filename_prefix()),
            pass_param(name='committish'),
            pass_param(name='gardenlinux_epoch'),
            pass_param(name='snapshot_timestamp'),
            pass_param(name='cicd_cfg_name'),
        ],
        runAfter=run_after,
    )


def mk_pipeline(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
    cicd_cfg_name: str,
    pipeline_flavour: glci.model.PipelineFlavour=glci.model.PipelineFlavour.SNAPSHOT,
):
    gardenlinux_flavours = set(gardenlinux_flavours) # mk unique


    tasks = []
    workspaces = []

    for idx,glf in enumerate(gardenlinux_flavours):
        workspace = Workspace(
            name='ws',
            workspace=f'ws-{idx}',
        )
        workspaces.append(workspace)

        clone_task = mk_clone_task(
            gardenlinux_flavour=glf,
            workspace=workspace
        )
        build_task = mk_pipeline_task(
            gardenlinux_flavour=glf,
            pipeline_flavour=pipeline_flavour,
            workspace=workspace,
            run_after=[clone_task.name]
        )
        tasks.extend((clone_task, build_task))

    pipeline = Pipeline(
        metadata=PipelineMetadata(
            name='build-gardenlinux-snapshot-pipeline',
            namespace='gardenlinux-tkn',
        ),
        spec=PipelineSpec(
            params=[
                NamedParam(name='committish'),
                NamedParam(name='gardenlinux_epoch'),
                NamedParam(name='snapshot_timestamp'),
                NamedParam(name='cicd_cfg_name'),
            ],
            workspaces=[
                NamedParam(name=workspace.workspace) for workspace in workspaces
            ],
            tasks=tasks,
        ),
    )

    return pipeline


def render_pipeline_dict(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
    cicd_cfg_name: str,
):
    gardenlinux_flavours = set(gardenlinux_flavours) # mk unique
    pipeline:dict = mk_pipeline(
        gardenlinux_flavours=gardenlinux_flavours,
        cicd_cfg_name=cicd_cfg_name,
    )

    return pipeline


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pipeline_cfg',
        default=paths.flavour_cfg_path,
    )
    parser.add_argument(
        '--flavour-set',
        default='all',
    )
    parser.add_argument(
        '--cicd-cfg',
        default='default',
    )
    parser.add_argument(
        '--outfile',
        default='pipeline.yaml',
    )
    parsed = parser.parse_args()

    build_yaml = parsed.pipeline_cfg

    flavour_set = glci.util.flavour_set(
        flavour_set_name=parsed.flavour_set,
        build_yaml=build_yaml,
    )

    gardenlinux_flavours = tuple(flavour_set.flavours())
    outfile = parsed.outfile

    pipeline:dict = render_pipeline_dict(
        gardenlinux_flavours=gardenlinux_flavours,
        cicd_cfg_name=parsed.cicd_cfg,
    )

    with open(outfile, 'w') as f:
        yaml.safe_dump(dataclasses.asdict(pipeline), f)

    print(f'dumped pipeline with {len(gardenlinux_flavours)} task(s) to {outfile}')

if __name__ == '__main__':
    main()
