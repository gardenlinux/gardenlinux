#!/usr/bin/env python3

import dacite
import dataclasses
import itertools
import typing

import yaml

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

    feature_names = ','.join(
        e.value for e in (
            gardenlinux_flavour.platform,
            *gardenlinux_flavour.extensions,
            *gardenlinux_flavour.modifiers,
        )
    )

    upload_prefix = f'snapshot/{gardenlinux_flavour.architecture.value}/'

    return PipelineTask(
        name=gardenlinux_flavour.canonical_name_prefix().replace('/', '-').replace('_', '-'),
        taskRef=TaskRef(name='build-gardenlinux-task'), # hardcode name for now
        params=[
            NamedParam(name='features', value=feature_names),
            NamedParam(name='uploadprefix', value=upload_prefix),
        ],
    )


def mk_pipeline(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour]
    pipeline_flavour: glci.model.PipelineFlavour=glci.model.PipelineFlavour.SNAPSHOT,
):
    gardenlinux_flavours = set(gardenlinux_flavours) # mk unique
    pipeline = Pipeline(
        metadata=PipelineMetadata(
            name='build-gardenlinux-snapshot-pipeline',
            namespace='gardenlinux-tkn',
        ),
        spec=PipelineSpec(
            tasks=[
            mk_pipeline_task(
                gardenlinux_flavour=glf,
                pipeline_flavour=pipeline_flavour,
            ),
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


def enumerate_build_flavours(build_yaml: str='../build.yaml'):
    with open(build_yaml) as f:
        parsed = yaml.safe_load(f)

    GardenlinuxFlavour = glci.model.GardenlinuxFlavour
    GardenlinuxFlavourCombination = glci.model.GardenlinuxFlavourCombination
    Architecture = glci.model.Architecture
    Platform = glci.model.Platform
    Extension = glci.model.Extension
    Modifier = glci.model.Modifier

    flavour_combinations = [
        dacite.from_dict(
            data_class=GardenlinuxFlavourCombination,
            data=flavour_def,
            config=dacite.Config(
                cast=[Architecture, Platform, Extension, Modifier, typing.Tuple],
            )
        ) for flavour_def in parsed['flavours']
    ]
    for comb in flavour_combinations:
        for arch, platf, exts, mods in itertools.product(
            comb.architectures,
            comb.platforms,
            comb.extensions,
            comb.modifiers,
        ):
            yield GardenlinuxFlavour(
                architecture=arch,
                platform=platf,
                extensions=exts,
                modifiers=mods,
                # fails=comb.fails, # not part of variant
            )


def main():
    gardenlinux_flavours = list(enumerate_build_flavours())
    outfile = 'pipeline.yaml'

    pipeline:dict = render_pipeline_dict(
        gardenlinux_flavours=gardenlinux_flavours,
    )

    with open(outfile, 'w') as f:
        yaml.safe_dump(dataclasses.asdict(pipeline), f)

    print(f'dumped pipeline with {len(gardenlinux_flavours)} task(s) to {outfile}')

if __name__ == '__main__':
    main()
