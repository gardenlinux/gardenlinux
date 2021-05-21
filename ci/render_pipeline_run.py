#!/usr/bin/env python3

import argparse
import dataclasses
import os
import subprocess
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

    if publishing_actions:
        name_parts = (
            pipeline_name[:len('gardenlinux')],
            '-'.join((a.value[:6].replace('_', '-') for a in publishing_actions)),
            version.replace('.', '-'),
            committish[:6],
        )
    else:
        name_parts = (
            pipeline_name[:11],
            version.replace('.', '-'),
            committish[:6],
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

def get_deb_build_image(
    oci_path: str,
    version_label: str,
):
    return f'{oci_path}/gardenlinux-build-deb:{version_label}'
    # for fixed path from concourse buildimage pipeline
    # return 'eu.gcr.io/gardener-project/gardenlinux/gardenlinux-build-deb:413.0.0'

def mk_pipeline_packages_run(
    branch: str,
    cicd_cfg: str,
    committish: str,
    gardenlinux_epoch: int,
    git_url: str,
    pipeline_name: str,
    publishing_actions: typing.Sequence[glci.model.PublishingAction],
    oci_path: str,
    version: str,
    aws_key_id: str,
    aws_secret_key: str,
    node_selector: dict = {},
    security_context: dict = {},
):
    run_name = mk_pipeline_name(
        pipeline_name = pipeline_name,
        publishing_actions = publishing_actions,
        version = version,
        committish = committish,
    )
    version_label = get_version_label(version, committish)
    build_deb_image = get_deb_build_image(oci_path, version_label)
    snapshot_timestamp = glci.model.snapshot_date(gardenlinux_epoch=gardenlinux_epoch)
    plrun = PipelineRun(
        metadata=tkn.model.Metadata(
            name=run_name,
        ),
        spec=PipelineRunSpec(
            params=[
                NamedParam(
                    name='branch',
                    value=branch,
                ),
                NamedParam(
                    name='committish',
                    value=committish,
                ),
                NamedParam(
                    name='gardenlinux_epoch',
                    value=str(gardenlinux_epoch),  # tekton only knows str
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
                    name='publishing_actions',
                    value=','.join((a.value for a in publishing_actions))
                ),
                NamedParam(
                    name='giturl',
                    value=git_url,
                ),
                NamedParam(
                    name='ocipath',
                    value=oci_path,
                ),
                NamedParam(
                    name='version_label',
                    value=version_label,
                ),
                NamedParam(
                    name='gardenlinux_build_deb_image',
                    value=build_deb_image,
                ),                
            ],
            pipelineRef=PipelineRef(
                name=pipeline_name,
            ),
            podTemplate=PodTemplate(nodeSelector=node_selector, securityContext=security_context),
            workspaces=[],
        ),
    )
    return plrun


def mk_pipeline_run(
    branch: str,
    cicd_cfg: str,
    committish: str,
    flavour_set: glci.model.GardenlinuxFlavourSet,
    gardenlinux_epoch: int,
    git_url: str,
    pipeline_name: str,
    promote_target: glci.model.BuildType,
    publishing_actions: typing.Sequence[glci.model.PublishingAction],
    oci_path: str,
    version: str,
    node_selector: dict = {},
    security_context: dict = {},
):

    run_name = mk_pipeline_name(
        pipeline_name = pipeline_name,
        publishing_actions = publishing_actions,
        version = version,
        committish = committish,
    )

    version_label = get_version_label(version, committish)
    build_image = get_build_image(oci_path, version_label)
    build_deb_image = get_deb_build_image(oci_path, version_label)
    snapshot_timestamp = glci.model.snapshot_date(gardenlinux_epoch=gardenlinux_epoch)

    flavour_count = len(list(flavour_set.flavours()))
    if flavour_count == 0:
        flavour_count = 1  # at least one workspace must be created

    plrun = PipelineRun(
        metadata=tkn.model.Metadata(
            name=run_name,
        ),
        spec=PipelineRunSpec(
            params=[
                NamedParam(
                    name='branch',
                    value=branch,
                ),
                NamedParam(
                    name='committish',
                    value=committish,
                ),
                NamedParam(
                    name='gardenlinux_epoch',
                    value=str(gardenlinux_epoch),  # tekton only knows str
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
                    name='publishing_actions',
                    value=','.join((a.value for a in publishing_actions))
                ),
                NamedParam(
                    name='giturl',
                    value=git_url,
                ),
                NamedParam(
                    name='ocipath',
                    value=oci_path,
                ),
                NamedParam(
                    name='version_label',
                    value=version_label,
                ),
                NamedParam(
                    name='build_image',
                    value=build_image,
                ),
                NamedParam(
                    name='gardenlinux_build_deb_image',
                    value=build_deb_image,
                ),
                
            ],
            pipelineRef=PipelineRef(
                name=pipeline_name,
            ),
            podTemplate=PodTemplate(nodeSelector=node_selector, securityContext=security_context),
            workspaces=[],
        ),
    )
    return plrun


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
    parser.add_argument('--aws-key-id', default='TODO set AWS key id', help='AWS key id for uploading packages')
    parser.add_argument('--aws-secret-key', default='TODO: set AWS secret key', help='AWS secret key uploading packages')

    parsed = parser.parse_args()
    parsed.publishing_actions = set(parsed.publishing_actions)

    flavour_set = glci.util.flavour_set(
        flavour_set_name=parsed.flavour_set,
        build_yaml=parsed.pipeline_cfg,
    )

    if (version := parsed.version) is None:
        # if version is not specify, derive from worktree (i.e. VERSION file)
        version = glci.model.next_release_version_from_workingtree()

    # XXX hardcode pipeline names and flavour for now
    pipeline_run = mk_pipeline_packages_run(
        branch=parsed.branch,
        cicd_cfg=parsed.cicd_cfg,
        committish=parsed.committish,
        gardenlinux_epoch=parsed.gardenlinux_epoch,
        git_url=parsed.git_url,
        oci_path=parsed.oci_path,
        pipeline_name='gl-packages-build',
        publishing_actions=parsed.publishing_actions,
        version=version,
        aws_key_id= parsed.aws_key_id,
        aws_secret_key= parsed.aws_secret_key,
        security_context={'runAsUser': 0}
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile_packages, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-packages-run written to {parsed.outfile_packages}')

    # XXX hardcode pipeline names and flavour for now
    pipeline_run = mk_pipeline_run(
        branch=parsed.branch,
        cicd_cfg=parsed.cicd_cfg,
        committish=parsed.committish,
        flavour_set=flavour_set,
        gardenlinux_epoch=parsed.gardenlinux_epoch,
        git_url=parsed.git_url,
        oci_path=parsed.oci_path,
        pipeline_name='gardenlinux-build',
        promote_target=parsed.promote_target,
        publishing_actions=parsed.publishing_actions,
        version=version,
    )

    pipeline_run_dict = dataclasses.asdict(pipeline_run)

    with open(parsed.outfile, 'w') as f:
        yaml.safe_dump(pipeline_run_dict, f)

    print(f'pipeline-run written to {parsed.outfile}')


if __name__ == '__main__':
    main()
