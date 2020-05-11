#!/usr/bin/env python3

import argparse
import dacite
import dataclasses
import typing

import yaml

import paths
import glci.model
import tkn.model


GardenlinuxFlavour = glci.model.GardenlinuxFlavour

Pipeline = tkn.model.Pipeline
PipelineSpec = tkn.model.PipelineSpec
PipelineMetadata = tkn.model.PipelineMetadata
TaskRef = tkn.model.TaskRef
PipelineTask = tkn.model.PipelineTask
NamedParam = tkn.model.NamedParam


def mk_pipeline_task(
    gardenlinux_flavour: GardenlinuxFlavour,
    pipeline_flavour: glci.model.PipelineFlavour,
):
    if not pipeline_flavour is glci.model.PipelineFlavour.SNAPSHOT:
        raise NotImplementedError(pipeline_flavour)

    modifier_names = ','.join(gardenlinux_flavour.modifiers)

    upload_prefix = f'{gardenlinux_flavour.architecture.value}/'

    def pass_param(name: str):
        '''
        create a named-param that will propagate the parent's param value
        '''
        return NamedParam(name=name, value=f'$(params.{name})')

    return PipelineTask(
        name=gardenlinux_flavour.canonical_name_prefix().replace('/', '-').replace('_', '-'),
        taskRef=TaskRef(name='build-gardenlinux-task'), # hardcode name for now
        params=[
            NamedParam(name='platform', value=gardenlinux_flavour.platform),
            NamedParam(name='modifiers', value=modifier_names),
            NamedParam(name='uploadprefix', value=upload_prefix),
            NamedParam(name='fnameprefix', value=gardenlinux_flavour.filename_prefix()),
            pass_param(name='committish'),
            pass_param(name='aws_cfg_name'),
            pass_param(name='s3_bucket_name'),
        ],
    )


def mk_pipeline(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
    pipeline_flavour: glci.model.PipelineFlavour=glci.model.PipelineFlavour.SNAPSHOT,
):
    gardenlinux_flavours = set(gardenlinux_flavours) # mk unique
    pipeline = Pipeline(
        metadata=PipelineMetadata(
            name='build-gardenlinux-snapshot-pipeline',
            namespace='gardenlinux-tkn',
        ),
        spec=PipelineSpec(
            params=[
                NamedParam(name='committish'),
                NamedParam(name='aws_cfg_name'),
                NamedParam(name='s3_bucket_name'),
            ],
            tasks=[
                mk_pipeline_task(
                    gardenlinux_flavour=glf,
                    pipeline_flavour=pipeline_flavour,
                )
                for glf in gardenlinux_flavours
            ],
        ),
    )

    return pipeline


def render_pipeline_dict(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
):
    gardenlinux_flavours = set(gardenlinux_flavours) # mk unique
    pipeline:dict = mk_pipeline(gardenlinux_flavours=gardenlinux_flavours)

    return pipeline


def enumerate_build_flavours(build_yaml: str, flavour_set: str):
    with open(build_yaml) as f:
        parsed = yaml.safe_load(f)

    GardenlinuxFlavourSet = glci.model.GardenlinuxFlavourSet
    GardenlinuxFlavour = glci.model.GardenlinuxFlavour
    GardenlinuxFlavourCombination = glci.model.GardenlinuxFlavourCombination
    Architecture = glci.model.Architecture

    flavour_sets = [
        dacite.from_dict(
            data_class=GardenlinuxFlavourSet,
            data=flavour_set,
            config=dacite.Config(
                cast=[Architecture, typing.Tuple]
            )
        ) for flavour_set in parsed['flavour_sets']
    ]

    for fs in flavour_sets:
        if fs.name == flavour_set:
            yield from fs.flavours()
            return
    else:
        raise RuntimeError(f'not found: {flavour_set=}')


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
        '--outfile',
        default='pipeline.yaml',
    )
    parsed = parser.parse_args()

    build_yaml = parsed.pipeline_cfg

    gardenlinux_flavours = list(enumerate_build_flavours(
        build_yaml=build_yaml,
        flavour_set=parsed.flavour_set,
    ))
    outfile = parsed.outfile

    pipeline:dict = render_pipeline_dict(
        gardenlinux_flavours=gardenlinux_flavours,
    )

    with open(outfile, 'w') as f:
        yaml.safe_dump(dataclasses.asdict(pipeline), f)

    print(f'dumped pipeline with {len(gardenlinux_flavours)} task(s) to {outfile}')

if __name__ == '__main__':
    main()
