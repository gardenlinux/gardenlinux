import os

from string import Template

import ctx
import glci.model
import product.v2
import release


def _find_path_in_manifest(
    suffix: str,
    manifest: glci.model.OnlineReleaseManifest,
) -> glci.model.S3_ReleaseFile:
    return next(path for path in manifest.paths if path.suffix == suffix)


def _find_manifest_in_set(
    platform: str,
    manifest_set: glci.model.OnlineReleaseManifestSet,
) -> glci.model.OnlineReleaseManifest:
    return next(manifest for manifest in manifest_set.manifests if manifest.platform == platform)


def _get_download_url(
    suffix: str,
    platform: str,
    image_metadata_tag: str,
    manifest_set: glci.model.OnlineReleaseManifestSet,
):
    manifest = _find_manifest_in_set(
        platform=platform,
        manifest_set=manifest_set,
    )
    if manifest is None:
        print('Could not find release-manifest for platform {manifest}, skipping release.')
        return None

    path = _find_path_in_manifest(suffix, manifest)
    if path is None:
        print(f'Could not find path for platform {platform=}, skipping release.')
        return None

    if image_metadata_tag:
        image_metadata = getattr(manifest.published_image_metadata, image_metadata_tag)
    else:
        image_metadata = None

    return (
        path.name,
        f'https://gardenlinux.s3.eu-central-1.amazonaws.com/{path.s3_key}',
        image_metadata,
    )


def get_manifest(
    cicd_cfg_name: str,
    committish: str,
    flavour_set_name: str,
    gardenlinux_epoch: str,
    version: str,
) -> bool: # True on success else False:

    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    if not (build_cfg := cicd_cfg.build):
        raise RuntimeError(f"No package-build config found in cicd-config {cicd_cfg_name}")

    aws_cfg_name = cicd_cfg.build.aws_cfg_name
    s3_bucket_name = build_cfg.s3_bucket_name

    print(f'downloading release manifest from s3 {aws_cfg_name=} {s3_bucket_name=}')

    find_release_set = glci.util.preconfigured(
        func=glci.util.find_release_set,
        cicd_cfg=glci.util.cicd_cfg(cicd_cfg_name),
    )

    manifest = find_release_set(
        flavour_set_name=flavour_set_name,
        build_committish=committish,
        version=version,
        gardenlinux_epoch=gardenlinux_epoch,
        build_type=glci.model.BuildType.RELEASE,
        absent_ok=True,
    )
    return manifest


def make_release(
    cicd_cfg_name: str,
    ctx_repository_config_name: str,
    committish: str,
    flavour_set_name: str,
    gardenlinux_epoch: str,
    giturl: str,
    version: str,
    repo_dir: str,
) -> bool: # True if a release was created, False otherwise
    manifest_set = get_manifest(
        cicd_cfg_name=cicd_cfg_name,
        committish=committish,
        flavour_set_name=flavour_set_name,
        gardenlinux_epoch=gardenlinux_epoch,
        version=version,
    )
    if not manifest_set:
        print('Could not find release-manifest set, skipping release.')
        return False

    platform = 'ali'
    suffix = glci.util.virtual_image_artifact_for_platform(platform)
    name_ali, download_link_ali, ids_ali = _get_download_url(
        platform=platform,
        suffix=suffix,
        image_metadata_tag='published_alicloud_images',
        manifest_set=manifest_set
    )
    print(f'name: {name_ali}, url: {download_link_ali}')
    ids_ali = [f'- Region: {obj.region_id}, Image-Id: {obj.image_id}' for obj in ids_ali]
    ids_ali_formatted = '\n'.join(ids_ali)
    print(f'{ids_ali_formatted}')

    platform = 'aws'
    suffix = glci.util.virtual_image_artifact_for_platform(platform)
    name_aws, download_link_aws, ids_aws = _get_download_url(
        platform=platform,
        suffix=suffix,
        image_metadata_tag='published_aws_images',
        manifest_set=manifest_set
    )
    print(f'AWS: name: {name_aws}, url: {download_link_aws}')
    ids_aws = [f'- Region: {obj.aws_region_id}, Image-Id: {obj.ami_id}' for obj in ids_aws]
    ids_aws_formatted = '\n'.join(ids_aws)
    print(f'{ids_aws_formatted}')

    platform = 'azure'
    suffix = glci.util.virtual_image_artifact_for_platform(platform)
    name_azure, download_link_azure, id_azure = _get_download_url(
        platform=platform,
        suffix=suffix,
        image_metadata_tag='urn',
        manifest_set=manifest_set
    )
    print(f'Azure: name: {name_azure}, urL: {download_link_azure}, image-name: {id_azure}')

    platform = 'gcp'
    suffix = glci.util.virtual_image_artifact_for_platform(platform)
    name_gcp, download_link_gcp, id_gcp = _get_download_url(
        platform=platform,
        suffix=suffix,
        manifest_set=manifest_set,
        image_metadata_tag='gcp_image_name',
    )
    print(f'GCP: name: {name_gcp}, url: {download_link_gcp}, image-name: {id_gcp}')

    platform = 'openstack'
    suffix = glci.util.virtual_image_artifact_for_platform(platform)
    name_openstack, download_link_openstack, ids_openstack = _get_download_url(
        platform=platform,
        suffix=suffix,
        manifest_set=manifest_set,
        image_metadata_tag='published_openstack_images'
    )
    print(f'Openstack: name: {name_openstack}, url: {download_link_openstack}')

    platform = 'vmware'
    suffix = glci.util.virtual_image_artifact_for_platform(platform)
    name_vmware, download_link_vmware, ids_vmware = _get_download_url(
        platform=platform,
        suffix=suffix,
        manifest_set=manifest_set,
        image_metadata_tag=None
    )
    print(f'VMware: name: {name_vmware}, url: {download_link_vmware}')

    # Generate markdown:
    template_path = os.path.abspath(
        os.path.join(repo_dir, "ci/templates/github_release.md")
    )
    with open(template_path, 'r') as template_file:
        md_release_template = template_file.read()

    release_template = Template(md_release_template)
    values = {
        'features': '* n/a',
        'version': version,
        'ali_name': name_ali,
        'ali_url': download_link_ali,
        'ali_ids': ids_ali_formatted,
        'aws_name': name_aws,
        'aws_url': download_link_aws,
        'aws_ids': ids_aws_formatted,
        'azure_name': name_azure,
        'azure_url': download_link_azure,
        'azure_id': id_azure,
        'gcp_name': name_gcp,
        'gcp_url': download_link_gcp,
        'gcp_id': id_gcp,
        'openstack_name': name_openstack,
        'openstack_url': download_link_openstack,
        'vsphere_name': name_vmware,
        'vsphere_url': download_link_vmware,
    }
    release_descr = release_template.safe_substitute(values)

    # for development:
    # with open(os.path.join(repo_dir, 'github_release.md'), 'w') as out_file:
    #     out_file.write(release_descr)

    # create the Github release:
    gh_release = release.create_release(
        giturl=giturl,
        tag_name=f'{version}',
        target_commitish=committish,
        body=release_descr,
        draft=True,
        prerelease=False
    )

    # download component descriptor
    f = ctx.cfg_factory()
    cfg = f.ctx_repository(ctx_repository_config_name)
    ctx_repo_base_url = cfg.base_url()

    comp_descr = product.v2.download_component_descriptor_v2(
        component_name='github.com/gardenlinux/gardenlinux',
        component_version=version,
        ctx_repo_base_url=ctx_repo_base_url,
        cache_dir=None,
    )

    with open(os.path.join(repo_dir, 'component-descriptor'), 'w') as out_file:
        comp_descr.to_fobj(out_file)

    with open(os.path.join(repo_dir, 'component-descriptor')) as cd_file:
        gh_release.upload_asset(
            content_type='text/plain;charset=UTF-8',
            name='component-descriptor',
            asset=cd_file,
        )

    return True
