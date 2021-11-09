#!/usr/bin/env python3

'''
Promotes the specified build results (represented by build result manifests in S3).

An example being the promotion of a build snapshot to a daily build.
'''

import argparse
import concurrent.futures
import functools
import logging
import logging.config
import os
import sys
import typing

import glci.util
import glci.model

glci.util.configure_logging()

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--flavourset', default='all')
    parser.add_argument('--committish')
    parser.add_argument('--gardenlinux-epoch', type=int)
    parser.add_argument(
      '--build-target',
      action='append',
      type=glci.model.BuildTarget,
      dest='build_targets',
    )
    parser.add_argument('--version', required=True)
    parser.add_argument('--source', default='snapshots')
    parser.add_argument(
        '--target',
        type=glci.model.BuildType,
        default=glci.model.BuildType.SNAPSHOT
    )
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument('--allow-partial', default=False, action='store_true')

    return parser.parse_args()


def publish_image(
    release: glci.model.OnlineReleaseManifest,
    cicd_cfg: glci.model.CicdCfg,
) -> glci.model.OnlineReleaseManifest:
    print(f'running release for {release.platform=}')

    if release.platform == 'ali':
        publish_function = _publish_alicloud_image
        cleanup_function = _clean_alicloud_image
    elif release.platform == 'aws':
        publish_function = _publish_aws_image
        cleanup_function = _cleanup_aws
    elif release.platform == 'gcp':
        publish_function = _publish_gcp_image
        cleanup_function = None
    elif release.platform == 'azure':
        publish_function = _publish_azure_image
        cleanup_function = None
    elif release.platform == 'openstack':
        publish_function = _publish_openstack_image
        cleanup_function = None
    elif release.platform == 'oci':
        publish_function = _publish_oci_image
        cleanup_function = None
    else:
        print(f'do not know how to publish {release.platform=}, yet')
        return release

    try:
        return publish_function(release, cicd_cfg)
    except:
        import traceback
        traceback.print_exc()
        if not cleanup_function is None:
            cleanup_function(release, cicd_cfg)
        else:
            print(f'warning: do not know how to cleanup {release.platform=}')
        raise


def _publish_alicloud_image(release: glci.model.OnlineReleaseManifest,
                            cicd_cfg: glci.model.CicdCfg,
) -> glci.model.OnlineReleaseManifest:
    import ccc.alicloud
    import glci.model
    import glci.alicloud
    build_cfg = cicd_cfg.build
    alicloud_cfg_name = build_cfg.alicloud_cfg_name

    oss_auth = ccc.alicloud.oss_auth(alicloud_cfg=alicloud_cfg_name)
    acs_client = ccc.alicloud.acs_client(alicloud_cfg=alicloud_cfg_name)

    maker = glci.alicloud.AlicloudImageMaker(
        oss_auth, acs_client, release, cicd_cfg.build)

    import ccc.aws
    s3_client = ccc.aws.session(cicd_cfg.build.aws_cfg_name).client('s3')
    maker.cp_image_from_s3(s3_client)
    return maker.make_image()


def _clean_alicloud_image(release: glci.model.OnlineReleaseManifest,
                            cicd_cfg: glci.model.CicdCfg,
) -> glci.model.OnlineReleaseManifest:
    import ccc.alicloud
    import glci.model
    import glci.alicloud
    build_cfg = cicd_cfg.build
    alicloud_cfg_name = build_cfg.alicloud_cfg_name

    oss_auth = ccc.alicloud.oss_auth(alicloud_cfg=alicloud_cfg_name)
    acs_client = ccc.alicloud.acs_client(alicloud_cfg=alicloud_cfg_name)

    maker = glci.alicloud.AlicloudImageMaker(
        oss_auth, acs_client, release, cicd_cfg.build)

    return maker.delete_images()


def _publish_aws_image(release: glci.model.OnlineReleaseManifest,
                       cicd_cfg: glci.model.CicdCfg,
) -> glci.model.OnlineReleaseManifest:
    import glci.aws
    import ccc.aws
    mk_session = functools.partial(
        ccc.aws.session, aws_cfg=cicd_cfg.build.aws_cfg_name)
    return glci.aws.upload_and_register_gardenlinux_image(
        mk_session=mk_session,
        build_cfg=cicd_cfg.build,
        release=release,
    )

def _cleanup_aws(release: glci.model.OnlineReleaseManifest,
                       cicd_cfg: glci.model.CicdCfg,
) -> glci.model.OnlineReleaseManifest:
    import glci.aws
    import ccc.aws
    target_image_name = glci.aws.target_image_name_for_release(release=release)
    mk_session = functools.partial(
        ccc.aws.session, aws_cfg=cicd_cfg.build.aws_cfg_name
    )
    return glci.aws.unregister_images_by_name(
        mk_session=mk_session,
        image_name=target_image_name,
    )


def _publish_azure_image(release: glci.model.OnlineReleaseManifest,
                       cicd_cfg: glci.model.CicdCfg,
                       ) -> glci.model.OnlineReleaseManifest:
    import glci.az
    import glci.model
    import ccc.aws
    import ci.util

    s3_client = ccc.aws.session(cicd_cfg.build.aws_cfg_name).client('s3')
    cfg_factory = ci.util.ctx().cfg_factory()

    service_principal_cfg = cfg_factory.azure_service_principal(
        cicd_cfg.publish.azure.service_principal_cfg_name
    )
    service_principal_cfg_serialized = glci.model.AzureServicePrincipalCfg(
        **service_principal_cfg.raw
    )
    storage_account_cfg = cfg_factory.azure_storage_account(
        cicd_cfg.publish.azure.storage_account_cfg_name
    )
    storage_account_cfg_serialized = glci.model.AzureStorageAccountCfg(
        **storage_account_cfg.raw
    )

    azure_marketplace_cfg = glci.model.AzureMarketplaceCfg(
        publisher_id=cicd_cfg.publish.azure.publisher_id,
        offer_id=cicd_cfg.publish.azure.offer_id,
        plan_id=cicd_cfg.publish.azure.plan_id,
    )

    return glci.az.upload_and_publish_image(
        s3_client,
        service_principal_cfg=service_principal_cfg_serialized,
        storage_account_cfg=storage_account_cfg_serialized,
        marketplace_cfg=azure_marketplace_cfg,
        release=release,
        notification_emails=cicd_cfg.publish.azure.notification_emails,
    )


def _publish_gcp_image(release: glci.model.OnlineReleaseManifest,
                       cicd_cfg: glci.model.CicdCfg,
                       ) -> glci.model.OnlineReleaseManifest:
    import glci.gcp
    import ccc.aws
    import ccc.gcp
    import ci.util
    gcp_cfg = ci.util.ctx().cfg_factory().gcp(cicd_cfg.build.gcp_cfg_name)
    storage_client = ccc.gcp.cloud_storage_client(gcp_cfg)
    s3_client = ccc.aws.session(cicd_cfg.build.aws_cfg_name).client('s3')
    compute_client = ccc.gcp.authenticated_build_func(gcp_cfg)('compute', 'v1')
    return glci.gcp.upload_and_publish_image(
        storage_client=storage_client,
        s3_client=s3_client,
        compute_client=compute_client,
        gcp_project_name=gcp_cfg.project(),
        release=release,
        build_cfg=cicd_cfg.build,
    )


def _publish_oci_image(
    release: glci.model.OnlineReleaseManifest,
    cicd_cfg: glci.model.CicdCfg,
    release_build: bool = True,
) -> glci.model.OnlineReleaseManifest:
    import ccc.aws
    import glci.oci
    import ccc.oci

    oci_client = ccc.oci.oci_client()
    s3_client = ccc.aws.session(cicd_cfg.build.aws_cfg_name).client('s3')

    return glci.oci.publish_image(
        release=release,
        publish_cfg=cicd_cfg.publish.oci,
        s3_client=s3_client,
        oci_client=oci_client,
        release_build=release_build,
    )


def _publish_openstack_image(release: glci.model.OnlineReleaseManifest,
                       cicd_cfg: glci.model.CicdCfg,
                       ) -> glci.model.OnlineReleaseManifest:
    import glci.openstack_image
    import ccc.aws
    import ci.util

    s3_client = ccc.aws.session(cicd_cfg.build.aws_cfg_name).client('s3')
    cfg_factory = ci.util.ctx().cfg_factory()
    openstack_environments_cfg = cfg_factory.ccee(cicd_cfg.publish.openstack.environment_cfg_name)

    username = openstack_environments_cfg.credentials().username()
    password = openstack_environments_cfg.credentials().passwd()

    image_properties = cfg_factory._cfg_element(
        cfg_type_name='openstack_os_image',
        cfg_name=cicd_cfg.publish.openstack.image_properties_cfg_name,
    ).raw['properties']

    openstack_env_cfgs = tuple((
        glci.model.OpenstackEnvironment(
            project_name=project.name(),
            domain=project.domain(),
            region=project.region(),
            auth_url=project.auth_url(),
            username=username,
            password=password,
        ) for project in openstack_environments_cfg.projects()
    ))

    return glci.openstack_image.upload_and_publish_image(
        s3_client,
        openstack_environments_cfgs=openstack_env_cfgs,
        image_properties=image_properties,
        release=release,
    )


def promote(
    releases: typing.Sequence[glci.model.OnlineReleaseManifest],
    target_prefix: str,
    build_committish: str,
    gardenlinux_epoch: int,
    version_str: str,
    build_targets: typing.Set[glci.model.BuildTarget],
    cicd_cfg: glci.model.CicdCfg,
    flavour_set: glci.model.GardenlinuxFlavourSet,
    build_type: glci.model.BuildType,
):

    if glci.model.BuildTarget.BUILD in build_targets:
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=len(releases))
        _publish_img = functools.partial(publish_image, cicd_cfg=cicd_cfg)

        print(f'running {len(releases)} publishing jobs in parallel')
        releases = tuple(executor.map(_publish_img, releases))

        for release in releases:
            print(release.published_image_metadata)

        if glci.model.BuildTarget.MANIFEST in build_targets:
            upload_release_manifest_set = glci.util.preconfigured(
                func=glci.util.upload_release_manifest_set,
                cicd_cfg=cicd_cfg,
            )

            manifest_set = glci.model.ReleaseManifestSet(
                manifests=releases,
                flavour_set_name=flavour_set.name,
            )

            manifest_path = os.path.join(
                target_prefix,
                glci.util.release_set_manifest_name(
                    build_committish=build_committish,
                    gardenlinux_epoch=gardenlinux_epoch,
                    version=version_str,
                    flavourset_name=flavour_set.name,
                    build_type=build_type,
                ),
            )

            upload_release_manifest_set(
                key=manifest_path,
                manifest_set=manifest_set,
            )

            print(f'uploaded manifest-set: {manifest_path=}')


def main():
    parsed = parse_args()

    cicd_cfg = glci.util.cicd_cfg(cfg_name=parsed.cicd_cfg)
    flavour_set = glci.util.flavour_set(flavour_set_name=parsed.flavourset)
    flavours = set(flavour_set.flavours())
    committish = parsed.committish
    gardenlinux_epoch = parsed.gardenlinux_epoch
    version = parsed.version or f'{gardenlinux_epoch}-{committish[0:6]}'

    find_releases = glci.util.preconfigured(
        func=glci.util.find_releases,
        cicd_cfg=cicd_cfg,
    )

    # XXX hard-code version naming convention
    build_version = f'{gardenlinux_epoch}-{committish[:6]}'

    releases = tuple(find_releases(
        flavour_set=flavour_set,
        version=build_version,
        build_committish=committish,
        gardenlinux_epoch=gardenlinux_epoch,
        prefix=glci.model.ReleaseManifest.manifest_key_prefix,
        )
    )

    is_complete = len(releases) == len(flavours)
    logger.info(f'{flavour_set.name=} contains {len(flavours)} flavours')
    logger.info(f'found {len(releases)} matching release(s) {is_complete=}')

    if not is_complete:
        logger.warning('Release is not complete')
        if not parsed.allow_partial:
            logger.error(f'{parsed.allow_partial=} -> aborting')
            sys.exit(1)

    promote(
        releases=releases,
        build_committish=committish,
        gardenlinux_epoch=gardenlinux_epoch,
        target_prefix=os.path.join(
            glci.model.ReleaseManifestSet.release_manifest_set_prefix,
            parsed.target.value,
        ),
        version_str=version,
        build_targets=parsed.build_targets,
        cicd_cfg=cicd_cfg,
        flavour_set=flavour_set,
        build_type=parsed.target,
    )


if __name__ == '__main__':
    main()
