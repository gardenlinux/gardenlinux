#!/usr/bin/env python3

import argparse
import dataclasses
import time
import typing
import yaml

import glci.model
import glci.util
import tkn.model
import paths

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
    publishing_actions: typing.Sequence[glci.model.PublishingAction],
    version: str,
    committish: str,
):
    def _publishing_action_shorthand(publishing_action):
        if publishing_action is glci.model.PublishingAction.RELEASE:
            return 'rel'
        elif publishing_action is glci.model.PublishingAction.RELEASE_CANDIDATE:
            return 'rc'
        elif publishing_action is glci.model.PublishingAction.BUILD_ONLY:
            return 'bo'
        elif publishing_action is glci.model.PublishingAction.IMAGES:
            return 'imgs'
        elif publishing_action is glci.model.PublishingAction.MANIFESTS:
            return 'man'
        elif publishing_action is glci.model.PublishingAction.COMPONENT_DESCRIPTOR:
            return 'cd'
        elif publishing_action is glci.model.PublishingAction.RUN_TESTS:
            return 'tst'

    # add last 4 seconds of time since epoch (to avoid issues with identical pipeline names for
    # repeated builds of the same commit)
    build_ts = str(int(time.time()))[-4:]
    if publishing_actions:
        name_parts = (
            pipeline_name[:11],
            '-'.join([_publishing_action_shorthand(a) for a in publishing_actions]),
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


def get_build_image(
    oci_path: str,
    version_label: str,
):
    return f'{oci_path}/gardenlinux-build-image:{version_label}'


def get_step_image(
    oci_path: str,
    version_label: str,
):
    return f'{oci_path}/gardenlinux-step-image:{version_label}'


def get_deb_build_image(
    oci_path: str,
    version_label: str,
):
    return f'{oci_path}/gardenlinux-build-deb:{version_label}'
    # for fixed path from concourse buildimage pipeline
    # return 'eu.gcr.io/gardener-project/gardenlinux/gardenlinux-build-deb:413.0.0'


def get_version(
    args: typing.Dict[str, str]
):
    if 'version' in args and args['version']:
        version = args['version']
    else:
        version = glci.model.next_release_version_from_workingtree()
    return version


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
    version = get_version(args)
    version_label = get_version_label(version, args['committish'])

    parsed_version = version_lib.parse_to_semver(version_label)
    if parsed_version.minor > 0:
        base_version_label = f'rel-{parsed_version.major}'
        print(f'Use base images tagged for release: {parsed_version.major}: {base_version_label}')
    else:
        base_version_label = 'latest'

    # check if to use an older existing base image or base image from currrent commit:
    if 'gardenlinux_base_image' in args and args['gardenlinux_base_image']:
        print('Found gardenlinux_base_image in args, force using base-image: '
            f'{args["gardenlinux_base_image"]}')
        path, label = args['gardenlinux_base_image'].split(':')
        build_deb_image = path + '/gardenlinux-build-deb:' + label
        build_image = path + '/gardenlinux-build-image:' + label
    else:
        build_deb_image = get_deb_build_image(args['oci_path'], base_version_label)
        build_image = get_build_image(args['oci_path'], base_version_label)

    step_image = get_step_image(args['oci_path'], base_version_label)
    # for git-url rename arg git_url to giturl:
    git_url_param = NamedParam(name='giturl', value=str(args['git_url']))

    params = [
        get_param_from_arg(args, 'additional_recipients'),
        get_param_from_arg(args, 'branch'),
        NamedParam(name='build_image', value=build_image),
        NamedParam(name='step_image', value=step_image),
        NamedParam(name='cicd_cfg_name', value=args['cicd_cfg']),
        get_param_from_arg(args, 'committish'),
        get_param_from_arg(args, 'disable_notifications'),
        NamedParam(name='gardenlinux_build_deb_image', value=build_deb_image),
        get_param_from_arg(args, 'gardenlinux_epoch'),
        get_param_from_arg(args, 'oci_path'),
        get_param_from_arg(args, 'only_recipients'),
        NamedParam(
            name='publishing_actions',
            value=','.join(a.value for a in args['publishing_actions'])
        ),
        NamedParam(
            name='snapshot_timestamp',
            value=glci.model.snapshot_date(gardenlinux_epoch=args['gardenlinux_epoch']),
        ),
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
        publishing_actions=args.publishing_actions,
        version=get_version(vars(args)),
        committish=args.committish,
    )

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


def mk_pipeline_packages_run(
    args: argparse.ArgumentParser,
    node_selector: dict = {},
    security_context: dict = {},
):
    params = get_common_parameters(vars(args))
    params.append(NamedParam(name='key_config_name', value='gardenlinux'))

    return mk_pipeline_run(
        pipeline_name='gl-packages-build',
        args=args,
        params=params,
        node_selector=node_selector,
        security_context=security_context,
        timeout='12h',
    )


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
        NamedParam(name='flavourset', value=flavour_set.name),
        NamedParam(name='promote_target', value=args.promote_target.value),
        NamedParam(name='pytest_cfg', value=args.pytest_cfg),
    ))
    build_image = get_build_image(args.oci_path, find_param('version_label', params).value)
    params.append(NamedParam(name='build_image', value=build_image))

    return mk_pipeline_run(
        pipeline_name='gardenlinux-build',
        args=args,
        params=params,
        node_selector=node_selector,
        security_context=security_context
    )


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
    parser.add_argument('--pipeline-cfg', default=paths.flavour_cfg_path)
    parser.add_argument('--outfile', default='pipeline_run.yaml')
    parser.add_argument('--outfile-packages', default='pipeline_package_run.yaml')
    parser.add_argument('--oci-path', default='eu.gcr.io/gardener-project/test/gardenlinux-test')
    parser.add_argument('--git-url', default='https://github.com/gardenlinux/gardenlinux.git')
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
        '--publishing-action',
        type=lambda x: (glci.model.PublishingAction(v) for v in x.split(',')),
        action='extend',
        dest='publishing_actions',
        default=[glci.model.PublishingAction.MANIFESTS],
    )

    parsed = parser.parse_args()
    parsed.publishing_actions = set(parsed.publishing_actions)

    pipeline_run = mk_pipeline_packages_run(
        args=parsed,
        security_context={'runAsUser': 0},
    )
    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile_packages, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-packages-run written to {parsed.outfile_packages}')

    pipeline_run = mk_pipeline_main_run(
        args=parsed,
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()
