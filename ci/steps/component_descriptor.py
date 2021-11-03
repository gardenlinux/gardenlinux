import dataclasses
import logging
import pprint
import sys
import typing

import glci
import glci.util
import glci.model

import gci.componentmodel as cm
import glci.s3
import version as version_util
import product.v2

import ctx

logger = logging.getLogger(__name__)


def _resolve_ctx_repository_config(cfg_name):
    f = ctx.cfg_factory()
    cfg = f.ctx_repository(cfg_name)
    return cfg.base_url()


def _virtual_image_packages(release_manifest, cicd_cfg):
    s3_client = glci.s3.s3_client(cicd_cfg)
    manifest_file_path = release_manifest.path_by_suffix('rootfs.manifest')
    resp = s3_client.get_object(
        Bucket=manifest_file_path.s3_bucket_name,
        Key=manifest_file_path.s3_key,
    )
    for line in resp['Body'].iter_lines():
        yield line.decode('utf-8')


def _calculate_effective_version(
    version: str,
    build_targets: typing.Set[glci.model.BuildTarget],
    committish: str,
) -> str:
    if glci.model.BuildTarget.FREEZE_VERSION in build_targets:
        return version
    else:
        return f'{version}-{committish}'


def build_component_descriptor(
    version: str,
    committish: str,
    cicd_cfg_name: str,
    gardenlinux_epoch: str,
    build_targets: str,
    ctx_repository_config_name: str,
    branch: str,
    snapshot_ctx_repository_config_name: str = None,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if glci.model.BuildTarget.COMPONENT_DESCRIPTOR not in build_target_set:
        print(
            f'{glci.model.BuildTarget.COMPONENT_DESCRIPTOR} not specified '
            'exiting now'
        )
        sys.exit(0)

    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    flavour_set = glci.util.flavour_set(flavour_set_name='all')

    find_releases = glci.util.preconfigured(
        func=glci.util.find_releases,
        cicd_cfg=cicd_cfg,
    )

    # effective version is used to incorporate into component-descriptor
    # (may deviate from gardenlinux-versions, which are always "final")
    effective_version = _calculate_effective_version(
        version=version,
        build_targets=build_target_set,
        committish=committish,
    )

    releases = tuple(find_releases(
        flavour_set=flavour_set,
        version=version,
        build_committish=committish,
        gardenlinux_epoch=int(gardenlinux_epoch),
        prefix=glci.model.ReleaseManifest.manifest_key_prefix,
        )
    )
    releases: typing.Tuple[glci.model.OnlineReleaseManifest]

    base_url = _resolve_ctx_repository_config(ctx_repository_config_name)
    if snapshot_ctx_repository_config_name:
        snapshot_repo_base_url = _resolve_ctx_repository_config(snapshot_ctx_repository_config_name)
    else:
        snapshot_repo_base_url = None

    component_descriptor = _base_component_descriptor(
        version=effective_version,
        branch=branch,
        commit=committish,
        ctx_repository_base_url=base_url
    )

    component_descriptor.component.resources = [
        virtual_machine_image_resource(
            release_manifest=release_manifest,
            cicd_cfg=cicd_cfg,
            effective_version=effective_version,
        )
        for release_manifest in releases
    ]

    component_descriptor.component.resources.extend(
        oci_image_resources(
            releases=releases,
            effective_version=effective_version,
        )
    )

    logger.info(
        'Generated Component-Descriptor:\n'
        f'{pprint.pformat(dataclasses.asdict(component_descriptor))}'
    )

    if glci.model.BuildTarget.COMPONENT_DESCRIPTOR in build_target_set:
        product.v2.upload_component_descriptor_v2_to_oci_registry(
            component_descriptor_v2=component_descriptor,
            on_exist=product.v2.UploadMode.OVERWRITE,
        )

    if snapshot_repo_base_url:
        if base_url != snapshot_repo_base_url:
            repo_ctx = cm.OciRepositoryContext(
                baseUrl=snapshot_repo_base_url,
                type=cm.AccessType.OCI_REGISTRY,
            )
            component_descriptor.component.repositoryContexts.append(repo_ctx)

        # upload obeys the appended repo_ctx
        product.v2.upload_component_descriptor_v2_to_oci_registry(
            component_descriptor_v2=component_descriptor,
            on_exist=product.v2.UploadMode.OVERWRITE,
        )


def oci_image_resources(
    releases: typing.List[glci.model.OnlineReleaseManifest],
    effective_version: str,
):
    for release_manifest in releases:
        if (
            release_manifest.platform == 'oci'
            and (meta := release_manifest.published_image_metadata)
        ):
            yield cm.Resource(
                name='gardenlinux',
                version=effective_version,
                type=cm.ResourceType.OCI_IMAGE,
                relation=cm.ResourceRelation.LOCAL,
                access=cm.OciAccess(
                    type=cm.AccessType.OCI_REGISTRY,
                    imageReference=meta.image_reference,
                ),
                labels=[
                    cm.Label(
                        name='gardener.cloud/gardenlinux/ci/build-metadata',
                        value={
                            'modifiers': release_manifest.modifiers,
                        }
                    ),
                ]
            )


def virtual_machine_image_resource(
    release_manifest: glci.model.OnlineReleaseManifest,
    cicd_cfg,
    effective_version: str,
):
    resource_type = 'virtual_machine_image'
    image_file_suffix = glci.util.virtual_image_artifact_for_platform(release_manifest.platform)
    image_file_path = release_manifest.path_by_suffix(image_file_suffix)

    bucket_name = cicd_cfg.build.s3_bucket_name

    labels = [
        cm.Label(
          name='gardener.cloud/gardenlinux/ci/build-metadata',
          value={
              'modifiers': release_manifest.modifiers,
              'buildTimestamp': release_manifest.build_timestamp,
              'debianPackages': [p for p in _virtual_image_packages(release_manifest, cicd_cfg)],
          }
        ),
    ]

    if (published_image_metadata := release_manifest.published_image_metadata):
        labels.append(
            cm.Label(
                name='gardener.cloud/gardenlinux/ci/published-image-metadata',
                value=published_image_metadata,
            ),
        )

    resource_access = cm.S3Access(
        type=cm.AccessType.S3,
        bucketName=bucket_name,
        objectKey=image_file_path.s3_key,
    )

    return cm.Resource(
        name='gardenlinux',
        version=effective_version,
        extraIdentity={
            'feature-flags': ','.join(release_manifest.modifiers),
            'architecture': release_manifest.architecture,
            'platform': release_manifest.platform,
        },
        type=resource_type,
        labels=labels,
        access=resource_access,
    )


def _base_component_descriptor(
    version: str,
    ctx_repository_base_url: str,
    commit: str,
    branch: str,
    component_name: str='github.com/gardenlinux/gardenlinux',
):
    parsed_version = version_util.parse_to_semver(version)
    if parsed_version.finalize_version() == parsed_version:
        # "final" version --> there will be a tag, later
        src_ref = f'refs/tags/{version}'
    else:
        src_ref = f'refs/heads/{branch}'

    # logical names must not contain slashes or dots
    logical_name = component_name.replace('/', '_').replace('.', '_')

    base_descriptor_v2 = cm.ComponentDescriptor(
        meta=cm.Metadata(schemaVersion=cm.SchemaVersion.V2),
        component=cm.Component(
            name=component_name,
            version=version,
            repositoryContexts=[
                cm.OciRepositoryContext(
                    baseUrl=ctx_repository_base_url,
                    type=cm.AccessType.OCI_REGISTRY,
                )
            ],
            provider=cm.Provider.INTERNAL,
            sources=[
                cm.ComponentSource(
                    name=logical_name,
                    type=cm.SourceType.GIT,
                    access=cm.GithubAccess(
                        type=cm.AccessType.GITHUB,
                        repoUrl=component_name,
                        ref=src_ref,
                        commit=commit,
                    ),
                    version=version,
                )
            ],
            componentReferences=[],
            resources=[], # added later
        ),
    )
    return base_descriptor_v2
