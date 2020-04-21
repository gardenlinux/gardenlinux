import dataclasses
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
):
    feature_names = ','.join(
        e.value for e in (
            gardenlinux_flavour.platform,
            *gardenlinux_flavour.extensions,
            *gardenlinux_flavour.modifiers,
        )
    )
    return PipelineTask(
        name=gardenlinux_flavour.canonical_name_prefix().replace('/', '-'),
        taskRef=TaskRef(name='build-gardenlinux-task'), # hardcode name for now
        params=[
            NamedParam(name='features', value=feature_names),
            NamedParam(name='uploadprefix', value=gardenlinux_flavour.canonical_name_prefix()),
        ],
    )



def mk_pipeline(gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour]):
    gardenlinux_flavours = set(gardenlinux_flavours) # mk unique
    pipeline = Pipeline(
        metadata=PipelineMetadata(
            name='build-gardenlinux-snapshot-pipeline',
            namespace='gardenlinux-tkn',
        ),
        spec=PipelineSpec(
            tasks=[
            mk_pipeline_task(gardenlinux_flavour=glf)
            for glf in gardenlinux_flavours
            ],
        ),
    )

    return pipeline


def render_pipeline(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
    outfile: str,
):
    gardenlinux_flavours = set(gardenlinux_flavours) # mk unique
    pipeline = mk_pipeline(gardenlinux_flavours=gardenlinux_flavours)

    with open(outfile, 'w') as f:
        yaml.safe_dump(dataclasses.asdict(pipeline), f)

    print(f'dumped pipeline with {len(gardenlinux_flavours)} task(s) to {outfile}')
