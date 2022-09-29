#!/usr/bin/env python3

import argparse
import dataclasses
import time
import typing
import logging
import yaml

import glci.model
import glci.util
import tkn.model
import paths
import version as version_lib

logger = logging.getLogger(__name__)

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


# k8s only allows dns names / leng restriction applies
def mk_pipeline_name(
    pipeline_name: str,
    build_targets: typing.Set[glci.model.BuildTarget],
    version: str,
    committish: str,
):
    def _build_targets_shorthand(build_targets):
        result = ''
        if glci.model.BuildTarget.BUILD in build_targets:
            result += 'b'
        if glci.model.BuildTarget.MANIFEST in build_targets:
            result += 'm'
        if glci.model.BuildTarget.COMPONENT_DESCRIPTOR in build_targets:
            result += 'c'
        if glci.model.BuildTarget.TESTS in build_targets:
            result += 't'
        if glci.model.BuildTarget.PUBLISH in build_targets:
            result += 'p'
        if glci.model.BuildTarget.FREEZE_VERSION in build_targets:
            result += 'v'
        if glci.model.BuildTarget.GITHUB_RELEASE in build_targets:
            result += 'g'
        return result

    # add last 4 seconds of time since epoch (to avoid issues with identical pipeline names for
    # repeated builds of the same commit)
    build_ts = str(int(time.time()))[-4:]
    if build_targets:
        name_parts = (
            pipeline_name[:11],
            _build_targets_shorthand(build_targets),
            version.replace('.', '-'),
            committish[:6],
            build_ts,
        )
    else:
        name_parts = (
            pipeline_name[:11],
            version.replace('.', '-'),
            committish[:6],
            build_ts,
        )

    return '-'.join(name_parts)[:60]


def get_version_label(
    version: str,
    committish: str,
):
    return f'{version}-{committish}'


def get_step_image(
    oci_path: str,
    version_label: str,
):
    return f'{oci_path}/gardenlinux-step-image:{version_label}'

def get_version(
    args: typing.Dict[str, str]
):
    if 'version' in args and args['version']:
        version = args['version']
        gardenbuild_version = version
    else:
        version, gardenbuild_version = glci.model.next_release_version_from_workingtree()
    return version, gardenbuild_version


def get_param_from_arg(
    args: typing.Dict[str, str],
    key: str,
) -> NamedParam:
    if key in args:
        return NamedParam(name=key, value=str(args[key]))
    else:
        raise ValueError(f'Missing required argument --{key}')


def find_param(
    key: str,
    params: typing.Sequence[NamedParam],
) -> NamedParam:
    return [p for p in params if p.name == key][0]


def get_common_parameters(
    args: typing.Dict[str, str]
) -> typing.Sequence[NamedParam]:
    # if version is not specified, derive from worktree (i.e. VERSION file)
    version, gardenbuild_version = get_version(args)

    version_label = get_version_label(version, args['committish'])

    parsed_version = version_lib.parse_to_semver(version_label)
    if parsed_version.minor > 0:
        base_version_label = f'rel-{parsed_version.major}'
        print(f'Use base images tagged for release: {parsed_version.major}: {base_version_label}')
    else:
        base_version_label = 'latest'

    step_image = get_step_image(args['oci_path'], base_version_label)
    # for git-url rename arg git_url to giturl:
    git_url_param = NamedParam(name='giturl', value=str(args['git_url']))

    params = [
        get_param_from_arg(args, 'additional_recipients'),
        get_param_from_arg(args, 'branch'),
        NamedParam(name='step_image', value=step_image),
        NamedParam(name='cicd_cfg_name', value=args['cicd_cfg']),
        get_param_from_arg(args, 'committish'),
        get_param_from_arg(args, 'disable_notifications'),
        get_param_from_arg(args, 'gardenlinux_epoch'),
        git_url_param,
        get_param_from_arg(args, 'oci_path'),
        get_param_from_arg(args, 'only_recipients'),
        get_param_from_arg(args, 'pr_id'),
        NamedParam(
            name='build_targets',
            value=','.join(a.value for a in args['build_targets'])
        ),
        NamedParam(
            name='snapshot_timestamp',
            value=glci.model.snapshot_date(gardenlinux_epoch=args['gardenlinux_epoch']),
        ),
        NamedParam(name='gardenbuild_version', value=gardenbuild_version),
        NamedParam(name='version', value=version),
        NamedParam(name='version_label', value=version_label),
    ]
    return params


def mk_pipeline_run(
    pipeline_name: str,
    args: argparse.ArgumentParser,
    params: typing.Sequence[NamedParam],
    node_selector: dict = {},
    security_context: dict = {},
    timeout: str = '1h'
):
    run_name = mk_pipeline_name(
        pipeline_name=pipeline_name,
        build_targets=args.build_targets,
        version=get_version(vars(args))[0],
        committish=args.committish,
    )

    # check if build-targets are correct (exit early)
    glci.model.BuildTarget.check_requirements(args.build_targets)

    plrun = PipelineRun(
        metadata=tkn.model.Metadata(
            name=run_name,
        ),
        spec=PipelineRunSpec(
            params=params,
            pipelineRef=PipelineRef(
                name=pipeline_name,
            ),
            podTemplate=PodTemplate(nodeSelector=node_selector, securityContext=security_context),
            workspaces=[],
            timeout=timeout,
        ),
    )
    return plrun


def mk_pipeline_main_run(
    args: argparse.ArgumentParser,
    node_selector: dict = {},
    security_context: dict = {},
):
    flavour_set = glci.util.flavour_set(
        flavour_set_name=args.flavour_set,
        build_yaml=args.pipeline_cfg,
    )

    params = get_common_parameters(vars(args))
    params.extend((
        NamedParam(name='flavour_set_name', value=flavour_set.name),
        NamedParam(name='promote_target', value=args.promote_target.value),
        NamedParam(name='pytest_cfg', value=args.pytest_cfg),
    ))

    return mk_pipeline_run(
        pipeline_name='gardenlinux-build',
        args=args,
        params=params,
        node_selector=node_selector,
        security_context=security_context,
        timeout='2h',
    )


def mk_limits(
    name: str,
):
    limits = tkn.model.LimitRange(
        metadata=tkn.model.Metadata(
            name=name,
        ),
        spec=tkn.model.LimitSpec(
            limits=[
                tkn.model.Limits(
                    type='Container',
                    max=tkn.model.LimitObject(ephemeral_storage='128Gi'),
                    min=tkn.model.LimitObject(ephemeral_storage='16Gi'),
                    default=tkn.model.LimitObject(
                        ephemeral_storage='128Gi',
                        memory='24G',
                        cpu=16.0,
                    ),
                    defaultRequest=tkn.model.LimitObject(
                        ephemeral_storage='20Gi',
                        memory='4G',
                        cpu=1.0,
                    ),
                ),
            ],
        ),
    )
    return limits


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--committish', default='main')
    parser.add_argument('--branch', default='main')
    parser.add_argument(
        '--gardenlinux-epoch',
        default=glci.model.gardenlinux_epoch_from_workingtree(),
        help='the gardenlinux epoch defining the snapshot timestamp to build against',
    )
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--skip-cfssl-build', action='store_true')
    parser.add_argument('--pipeline-cfg', default=paths.flavour_cfg_path)
    parser.add_argument('--outfile', default='pipeline_run.yaml')
    parser.add_argument('--oci-path', default='eu.gcr.io/gardener-project/test/gardenlinux-test')
    parser.add_argument('--git-url', default='https://github.com/gardenlinux/gardenlinux.git')
    parser.add_argument('--pr-id', default=0)
    parser.add_argument('--flavour-set', default='all')
    parser.add_argument('--version', default=None)
    parser.add_argument('--disable-notifications', action='store_const', const=True, default=False)
    parser.add_argument('--additional-recipients', default=' ')
    parser.add_argument('--only-recipients', default=' ')
    parser.add_argument('--pytest-cfg', default='default')
    parser.add_argument(
        '--promote-target',
        type=glci.model.BuildType,
        default=glci.model.BuildType.SNAPSHOT,
    )
    parser.add_argument(
        '--build-targets',
        type=lambda x: (glci.model.BuildTarget(v) for v in x.split(',')),
        action='extend',
        dest='build_targets',
        # default=[glci.model.BuildTarget.MANIFEST],
    )
    parser.add_argument('--gardenlinux-base-image')

    parsed = parser.parse_args()
    parsed.build_targets = set(parsed.build_targets)

    limits = mk_limits(name='gardenlinux')
    limits_dict = dataclasses.asdict(limits, dict_factory=tkn.model.limits_asdict_factory)

    pipeline_run = mk_pipeline_main_run(
        args=parsed,
        security_context={'runAsUser': 0},
    )
    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    logger.info(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()
