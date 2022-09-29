#!/usr/bin/env python3

import dataclasses
import json
import typing
import logging

import yaml

import glci.model
import glci.util
import params
import tkn.model

logger = logging.getLogger(__name__)

GardenlinuxFlavour = glci.model.GardenlinuxFlavour

Pipeline = tkn.model.Pipeline
PipelineSpec = tkn.model.PipelineSpec
Metadata = tkn.model.Metadata
TaskRef = tkn.model.TaskRef
PipelineTask = tkn.model.PipelineTask
NamedParam = tkn.model.NamedParam
all_params = params.AllParams


def pass_param(name: str):
    '''
    create a named-param that will propagate the parent's param value
    '''
    return NamedParam(name=name, value=f'$(params.{name})')


def _get_modifier_names(gardenlinux_flavour):
    modifier_names = ','.join(
        sorted(
            (m.name for m in gardenlinux_flavour.calculate_modifiers())
        )
    )
    return modifier_names


def _generate_task_name(prefix: str, gardenlinux_flavour: GardenlinuxFlavour):
    task_name = prefix + gardenlinux_flavour.canonical_name_prefix().replace('/', '-')\
        .replace('_', '').strip('-')\
        .replace('readonly', 'ro')  # hardcoded shortening (length-restriction)

    if len(task_name) > 63:
        logger.warning(f'{task_name=} too long - will shorten')
        task_name = task_name[:63]
    return task_name


def _find_task(
    name: str,
    tasks: typing.Sequence[tkn.model.Task]
):
  return next(task for task in tasks if name == task.metadata.name)


def  _get_passed_parameters(
    name: str,
    all_tasks: typing.Sequence[tkn.model.Task],
    overrides: typing.Set[NamedParam] = None,
) -> typing.Sequence[NamedParam]:
    task_ref = _find_task(name=name, tasks=all_tasks)
   # generate default params for all task parameters just passing the value
    params = task_ref.spec.params
    params = dict((p.name, pass_param(name=p.name)) for p in params)
    # make a dict:
    if overrides:
        overrides = dict((p.name, p) for p in overrides)
        # merge both:
        params |= overrides
    # convert to a type that can be rendered as yaml
    return tuple(params.values())


def mk_pipeline_base_build_task(
    all_tasks: typing.Sequence[tkn.model.Task]
):
    name = "build-baseimage"
    params = _get_passed_parameters(
        name=name,
        all_tasks=all_tasks,
        overrides={
            NamedParam(name='pipeline_run_name', value='$(context.pipelineRun.name)'),
            NamedParam(name='namespace', value='$(context.pipelineRun.namespace)'),
        },
    )
    return PipelineTask(
        name=name,
        taskRef=TaskRef(name=name),
        params=tuple(params),
        runAfter=None,
    )


def mk_pipeline_build_task(
    gardenlinux_flavour: GardenlinuxFlavour,
    pipeline_flavour: glci.model.PipelineFlavour,
    run_after: typing.List[str],
    all_tasks: typing.Sequence[tkn.model.Task]
):
    if pipeline_flavour is not glci.model.PipelineFlavour.SNAPSHOT:
        raise NotImplementedError(pipeline_flavour)

    modifier_names = _get_modifier_names(gardenlinux_flavour)
    task_name = _generate_task_name(prefix='', gardenlinux_flavour=gardenlinux_flavour)
    task_ref_name = 'build-gardenlinux-task'

    params = _get_passed_parameters(
        name=task_ref_name,
        all_tasks=all_tasks,
        overrides={
            NamedParam(name='modifiers', value=modifier_names),
            NamedParam(name='platform', value=gardenlinux_flavour.platform),
         }
    )
    return PipelineTask(
        name=task_name,
        taskRef=TaskRef(name=task_ref_name),
        params=params,
        runAfter=run_after,
        timeout='2h'
    )


def mk_pipeline_test_task(
    gardenlinux_flavour: GardenlinuxFlavour,
    pipeline_flavour: glci.model.PipelineFlavour,
    run_after: typing.List[str],
    all_tasks: typing.Sequence[tkn.model.Task]
):

    modifier_names = _get_modifier_names(gardenlinux_flavour)
    task_name = _generate_task_name(prefix="tst", gardenlinux_flavour=gardenlinux_flavour)
    task_ref_name = 'integration-test-task'

    params = _get_passed_parameters(
        name=task_ref_name,
        all_tasks=all_tasks,
         overrides={
            NamedParam(name='modifiers', value=modifier_names),
            NamedParam(name='platform', value=gardenlinux_flavour.platform),
         }
    )
    return PipelineTask(
        name=task_name,
        taskRef=TaskRef(name=task_ref_name),
        params=params,
        runAfter=run_after,
    )


def mk_pipeline_promote_task(
    run_after: typing.List[str],
    all_tasks: typing.Sequence[tkn.model.Task]
):
    name = 'promote-gardenlinux-task'
    params = _get_passed_parameters(name=name, all_tasks=all_tasks)
    return PipelineTask(
        name=name,
        taskRef=TaskRef(name=name),
        params=params,
        runAfter=run_after,
    )


def mk_pipeline_notify_task(
    previous_tasks: typing.List[str],
    all_tasks: typing.Sequence[tkn.model.Task],
    build_tasks: typing.Sequence[tkn.model.Task],
    platform_set: typing.Set[str] = frozenset(),
):
    status_dict = {}

    for task in previous_tasks:
        status_dict['status_' + task.name] = f'$(tasks.{task.name}.status)'
    status_str = json.dumps(status_dict)

    build_task_names = ','.join([task.name for task in  build_tasks])
    platform_set_str = ','.join(platform_set)

    # generate default params for all task parameters just passing the value
    name = 'notify-task'
    params = _get_passed_parameters(
        name=name,
        all_tasks=all_tasks,
        overrides={
            NamedParam(name='platform_set', value=platform_set_str),
            NamedParam(name='pipeline_run_name', value='$(context.pipelineRun.name)'),
            NamedParam(name='pipeline_name', value='$(context.pipeline.name)'),
            NamedParam(name='namespace', value='$(context.pipelineRun.namespace)'),
            NamedParam(name='status_dict_str', value=status_str),
            NamedParam(name='build_tasks', value=build_task_names),
        }
    )

    return PipelineTask(
        name=name,
        taskRef=TaskRef(name=name),
        params=tuple(params), # convert set to make renderable to yaml
    )


def mk_pipeline(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
    all_tasks: typing.Sequence[tkn.model.Task],
    pipeline_flavour: glci.model.PipelineFlavour = glci.model.PipelineFlavour.SNAPSHOT,
):
    gardenlinux_flavours = set(gardenlinux_flavours)  # mk unique

    tasks = []

    # pre-build base images serving as container imager for further build steps:
    base_build_task = mk_pipeline_base_build_task(all_tasks)
    tasks.append(base_build_task)

    build_tasks = []
    test_tasks = []
    platform_set = set()
    # build gardenlinux in all flavours
    for glf in gardenlinux_flavours:
        build_task = mk_pipeline_build_task(
            gardenlinux_flavour=glf,
            pipeline_flavour=pipeline_flavour,
            run_after=[base_build_task.name],
            all_tasks=all_tasks,
        )
        build_tasks.append(build_task)
        test_task = mk_pipeline_test_task(
            gardenlinux_flavour=glf,
            pipeline_flavour=pipeline_flavour,
            run_after=[build_task.name],
            all_tasks=all_tasks,
        )
        test_tasks.append(test_task)
        platform_set.add(glf.platform)

    tasks += build_tasks
    tasks += test_tasks

    promote_task = mk_pipeline_promote_task(
        run_after=[plt.name for plt in build_tasks],
        all_tasks=all_tasks,
    )
    tasks.append(promote_task)

    task_ref = _find_task('notify-task', all_tasks)
    notify_task = mk_pipeline_notify_task(
        previous_tasks=tasks,
        build_tasks=build_tasks,
        all_tasks=all_tasks,
        platform_set=platform_set,
    )

    params = []
    params += task_ref.spec.params

    for task in tasks:
        matched_task = _find_task(task.taskRef.name, all_tasks)
        params += matched_task.spec.params

    # eliminitate all duplicates
    params = set(params)

    # remove some special parameters that are calculated
    params.remove(all_params.modifiers)
    params.remove(all_params.namespace)
    params.remove(all_params.platform)
    params.remove(all_params.pipeline_run_name)
    params.remove(all_params.pipeline_name)
    params.remove(all_params.platform_set)

    # convert to list as set is not rendered to yaml
    params = tuple(params)

    pipeline = Pipeline(
        metadata=Metadata(
            name='gardenlinux-build',
        ),
        spec=PipelineSpec(
            params=params,
            tasks=tasks,
            _finally=[notify_task, ],
        ),
    )

    return pipeline


def render_pipeline_dict(
    gardenlinux_flavours: typing.Sequence[GardenlinuxFlavour],
    tasks: typing.Sequence[tkn.model.Task]
):
    gardenlinux_flavours = set(gardenlinux_flavours)  # mk unique
    pipeline: dict = mk_pipeline(
        all_tasks=tasks,
        gardenlinux_flavours=gardenlinux_flavours,
    )

    return pipeline


def render_pipelines(
    build_yaml: str,
    flavour_set: str,
    outfile_pipeline_main: str,
    tasks: typing.Sequence[tkn.model.Task]
):
    flavour_set = glci.util.flavour_set(
        flavour_set_name=flavour_set,
        build_yaml=build_yaml,
    )

    # generate pipeline for gardenlinux build
    gardenlinux_flavours = set(flavour_set.flavours())

    pipeline: dict = render_pipeline_dict(
        gardenlinux_flavours=gardenlinux_flavours,
        tasks=tasks,
    )

    with open(outfile_pipeline_main, 'w') as f:
        pipeline_raw = dataclasses.asdict(pipeline)
        yaml.safe_dump_all((pipeline_raw,), stream=f)

    logger.info(
        f'dumped pipeline with {len(gardenlinux_flavours)} task(s) to {outfile_pipeline_main}'
    )
