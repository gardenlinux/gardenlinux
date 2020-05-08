#!/usr/bin/env python3

import argparse
import dacite
import dataclasses
import itertools
import os
import typing

import yaml

import glci.model
import tkn.model

own_dir = os.path.abspath(os.path.dirname(__file__))

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

    modifier_names = ','.join(e.value for e in gardenlinux_flavour.modifiers)

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
            NamedParam(name='platform', value=gardenlinux_flavour.platform.value),
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


def enumerate_build_flavours(build_yaml: str):
    with open(build_yaml) as f:
        parsed = yaml.safe_load(f)

    GardenlinuxFlavour = glci.model.GardenlinuxFlavour
    GardenlinuxFlavourCombination = glci.model.GardenlinuxFlavourCombination
    Architecture = glci.model.Architecture

    flavour_combinations = [
        dacite.from_dict(
            data_class=GardenlinuxFlavourCombination,
            data=flavour_def,
            config=dacite.Config(
                cast=[Architecture, typing.Tuple],
            )
        ) for flavour_def in parsed['flavours']
    ]
    for comb in flavour_combinations:
        for arch, platf, mods in itertools.product(
            comb.architectures,
            comb.platforms,
            comb.modifiers,
        ):
            yield GardenlinuxFlavour(
                architecture=arch,
                platform=platf,
                modifiers=mods,
                # fails=comb.fails, # not part of variant
            )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pipeline_cfg',
        default=os.path.join(own_dir, os.pardir, 'build.yaml'),
    )
    parser.add_argument(
        '--outfile',
        default='pipeline.yaml',
    )
    parsed = parser.parse_args()

    build_yaml = parsed.pipeline_cfg

    gardenlinux_flavours = list(enumerate_build_flavours(build_yaml=build_yaml))
    outfile = parsed.outfile

    pipeline:dict = render_pipeline_dict(
        gardenlinux_flavours=gardenlinux_flavours,
    )

    with open(outfile, 'w') as f:
        yaml.safe_dump(dataclasses.asdict(pipeline), f)

    print(f'dumped pipeline with {len(gardenlinux_flavours)} task(s) to {outfile}')

if __name__ == '__main__':
    main()
