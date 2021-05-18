#!/usr/bin/env python3

import argparse
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
Metadata = tkn.model.Metadata
TaskRef = tkn.model.TaskRef
PipelineTask = tkn.model.PipelineTask
NamedParam = tkn.model.NamedParam


def pass_param(name: str):
    '''
    create a named-param that will propagate the parent's param value
    '''
    return NamedParam(name=name, value=f'$(params.{name})')


def mk_pipeline_base_build_task(
):
    return PipelineTask(
        name="build-baseimage",
        taskRef=TaskRef(name='build-baseimage'),
        params=[
            pass_param(name='giturl'),
            pass_param(name='committish'),
            pass_param(name='ocipath'),
            pass_param(name='version_label'),
        ],
        runAfter=None,
    )

def mk_pipeline_package_build_task(
    package_name: str,
    run_after: typing.List[str],
):
    return PipelineTask(
        name=f'build-packages-{package_name.replace("_", "-").replace(".", "-")}',
        taskRef=TaskRef(name='build-packages'),
        params=[
            pass_param(name='giturl'),
            pass_param(name='committish'),
            pass_param(name='version_label'),
            NamedParam(name='pkg_name', value=package_name),
            pass_param(name='gardenlinux_build_deb_image'),
            pass_param(name='aws_key_id'),
            pass_param(name='aws_secret_key'),
            ],
        runAfter=run_after,
        timeout="6h"
    )

def mk_pipeline_build_task(
    gardenlinux_flavour: GardenlinuxFlavour,
    pipeline_flavour: glci.model.PipelineFlavour,
    run_after: typing.List[str],
):
    if pipeline_flavour is not glci.model.PipelineFlavour.SNAPSHOT:
        raise NotImplementedError(pipeline_flavour)

    modifier_names = ','.join(
        sorted(
            (m.name for m in gardenlinux_flavour.calculate_modifiers())
        )
    )

    task_name = gardenlinux_flavour.canonical_name_prefix().replace('/', '-')\
        .replace('_', '').strip('-')\
        .replace('readonly', 'ro')  # hardcoded shortening (length-restriction)

    if len(task_name) > 64:
        print(f'WARNING: {task_name=} too long - will shorten')
        task_name = task_name[:64]

    return PipelineTask(
        name=task_name,
        taskRef=TaskRef(name='build-gardenlinux-task'),  # hardcode name for now
        params=[
            pass_param(name='build_image'),
            pass_param(name='cicd_cfg_name'),
            pass_param(name='committish'),
            pass_param(name='flavourset'),
            pass_param(name='gardenlinux_epoch'),
            pass_param(name='giturl'),
            NamedParam(name='modifiers', value=modifier_names),
            NamedParam(name='platform', value=gardenlinux_flavour.platform),
            pass_param(name='promote_target'),
            pass_param(name='publishing_actions'),
            pass_param(name='snapshot_timestamp'),
            pass_param(name='version'),
        ],
        runAfter=run_after,
    )


def mk_pipeline_promote_task(
    run_after: typing.List[str],
):
    return PipelineTask(
        name='promote-gardenlinux-task',
        taskRef=TaskRef(name='promote-gardenlinux-task'),  # XXX unhardcode
        params=[
            pass_param(name='branch'),
            pass_param(name='cicd_cfg_name'),
            pass_param(name='committish'),
            pass_param(name='flavourset'),
            pass_param(name='gardenlinux_epoch'),
            pass_param(name='publishing_actions'),
            pass_param(name='snapshot_timestamp'),
            pass_param(name='version'),
        ],
        runAfter=run_after,
    )


def mk_pipeline_packages():
    tasks = []

    # pre-build base images serving as container imager for further build steps:
    base_build_task = mk_pipeline_base_build_task()
    tasks.append(base_build_task)

    # build packages:
    package_tasks = []
    for package in [
        'apt', 
        'cyrus-sasl2', 
        'dracut', 
        'ignition', 
        'iproute2', 
        'linux-5.10',
        'pam',
        'python3.9',
        'wireguard'
        ]:
        package_task = mk_pipeline_package_build_task(package, [base_build_task.name])
        package_tasks.append(package_task)
    
    run_after=[pkg.name for pkg in package_tasks]
    tasks += package_tasks

    pipeline = Pipeline(
        metadata=Metadata(
            name='gl-packages-build',
        ),
        spec=PipelineSpec(
            params=[
                NamedParam(name='branch'),
                NamedParam(name='gardenlinux_build_deb_image'),
                NamedParam(name='cicd_cfg_name'),
                NamedParam(name='committish'),
                NamedParam(name='gardenlinux_epoch'),
                NamedParam(name='giturl'),
                NamedParam(name='ocipath'),
                NamedParam(name='publishing_actions'),
                NamedParam(name='snapshot_timestamp'),
                NamedParam(name='version'),
                NamedParam(name='version_label'),
                NamedParam(name='aws_key_id'),
                NamedParam(name='aws_secret_key'),
            ],
            tasks=tasks,
        ),
    )

    return pipeline

    
def mk_pipeline(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
    pipeline_flavour: glci.model.PipelineFlavour = glci.model.PipelineFlavour.SNAPSHOT,
):
    gardenlinux_flavours = set(gardenlinux_flavours)  # mk unique

    tasks = []

    # pre-build base images serving as container imager for further build steps:
    base_build_task = mk_pipeline_base_build_task()
    tasks.append(base_build_task)

    build_tasks = []
    # build gardenlinux in all flavours
    for glf in gardenlinux_flavours:
        build_task = mk_pipeline_build_task(
            gardenlinux_flavour=glf,
            pipeline_flavour=pipeline_flavour,
            run_after= [ base_build_task.name ],
        )
        build_tasks.append(build_task)

    tasks += build_tasks

    promote_task = mk_pipeline_promote_task(
        run_after=[plt.name for plt in build_tasks],
    )
    tasks.append(promote_task)

    pipeline = Pipeline(
        metadata=Metadata(
            name='gardenlinux-build',
        ),
        spec=PipelineSpec(
            params=[
                NamedParam(name='branch'),
                NamedParam(name='build_image'),
                NamedParam(name='gardenlinux_build_deb_image'),
                NamedParam(name='cicd_cfg_name'),
                NamedParam(name='committish'),
                NamedParam(name='flavourset'),
                NamedParam(name='gardenlinux_epoch'),
                NamedParam(name='giturl'),
                NamedParam(name='ocipath'),
                NamedParam(name='promote_target'),
                NamedParam(name='publishing_actions'),
                NamedParam(name='snapshot_timestamp'),
                NamedParam(name='version'),
                NamedParam(name='version_label'),
            ],
            tasks=tasks,
        ),
    )

    return pipeline


def render_pipeline_dict(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
):
    gardenlinux_flavours = set(gardenlinux_flavours)  # mk unique
    pipeline: dict = mk_pipeline(
        gardenlinux_flavours=gardenlinux_flavours,
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
        '--outfile',
        default='pipeline.yaml',
    )
    parser.add_argument(
        '--outfile-packages',
        default='pipeline-packages.yaml',
    )
    parsed = parser.parse_args()

    build_yaml = parsed.pipeline_cfg

    flavour_set = glci.util.flavour_set(
        flavour_set_name=parsed.flavour_set,
        build_yaml=build_yaml,
    )


    # generate pipeline for packages:
    pipeline: dict = mk_pipeline_packages()
 
    with open(parsed.outfile_packages, 'w') as f:
        pipeline_raw = dataclasses.asdict(pipeline)
        yaml.safe_dump_all((pipeline_raw,), stream=f)

    print(f'dumped pipeline for packages to {parsed.outfile_packages}')

    # generate pipeline for gardenlinux build
    gardenlinux_flavours = set(flavour_set.flavours())
    outfile = parsed.outfile

    pipeline: dict = render_pipeline_dict(
        gardenlinux_flavours=gardenlinux_flavours,
    )
 
    with open(outfile, 'w') as f:
        pipeline_raw = dataclasses.asdict(pipeline)
        yaml.safe_dump_all((pipeline_raw,), stream=f)

    print(f'dumped pipeline with {len(gardenlinux_flavours)} task(s) to {outfile}')


if __name__ == '__main__':
    main()
