import dataclasses
import os
import sys

import glci.model
import glci.util
import promote
import version as version_util

parsable_to_int = str


def promote_single_step(
    cicd_cfg_name: str,
    committish: str,
    architecture: str,
    platform: str,
    gardenlinux_epoch: parsable_to_int,
    modifiers: str,
    version: str,
    publishing_actions: str,
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    publishing_actions = [
        glci.model.PublishingAction(action.strip()) for action in publishing_actions.split(',')
    ]
    if glci.model.PublishingAction.RELEASE_CANDIDATE not in publishing_actions:
        print(
            f'publishing action {glci.model.PublishingAction.RELEASE_CANDIDATE=} not specified'
            ' - exiting now'
        )
        sys.exit(0)

    find_release = glci.util.preconfigured(
        func=glci.util.find_release,
        cicd_cfg=cicd_cfg,
    )

    if platform not in glci.model.platform_names():
        raise ValueError(f'invalid value {platform=}')

    modifiers = glci.model.normalised_modifiers(
        platform=platform,
        modifiers=modifiers.split(','),
    )

    release_manifest = find_release(
        release_identifier=glci.model.ReleaseIdentifier(
            build_committish=committish,
            version=version,
            gardenlinux_epoch=int(gardenlinux_epoch),
            architecture=glci.model.Architecture(architecture),
            platform=platform,
            modifiers=tuple(modifiers),
        ),
    )

    if not release_manifest:
        raise ValueError('no release-manifest found')

    if release_manifest.published_image_metadata is not None:
        # XXX should actually check for completeness - assume for now there is
        # transactional semantics in place
        print('artifacts were already published - exiting now')
        sys.exit(0)

    if release_manifest.platform == 'azure':
        # publishing on azure is currently a lengthy process. We do, however, already know the URN
        # it will end up at.
        # Prepare the information here already - will be overwritten if actual publishing proceeds.
        publisher_id = cicd_cfg.publish.azure.publisher_id,
        offer_id = cicd_cfg.publish.azure.offer_id,
        plan_id = cicd_cfg.publish.azure.plan_id,
        parsed_version = version_util.parse_to_semver(version)
        published_image_metadata = glci.model.AzurePublishedImage(
            transport_state=glci.model.AzureTransportState.PROVISIONAL,
            publish_operation_id='',
            golive_operation_id='',
            urn=f'{publisher_id}:{offer_id}:{plan_id}:{parsed_version}',
        )
        dataclasses.replace(release_manifest, published_image_metadata=published_image_metadata)

    new_manifest = promote.publish_image(
        release=release_manifest,
        cicd_cfg=cicd_cfg,
    )

    # the (modified) release manifest contains the publishing resource URLs - re-upload to persist
    upload_release_manifest = glci.util.preconfigured(
        func=glci.util.upload_release_manifest,
        cicd_cfg=cicd_cfg,
    )

    manifest_key = new_manifest.canonical_release_manifest_key()

    upload_release_manifest(
        key=manifest_key,
        manifest=new_manifest,
    )


def promote_step(
    cicd_cfg_name: str,
    flavourset: str,
    publishing_actions: str,
    gardenlinux_epoch: parsable_to_int,
    committish: str,
    version: str,
    build_type: glci.model.BuildType = glci.model.BuildType.RELEASE,
):
    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    flavour_set = glci.util.flavour_set(flavourset)
    flavours = tuple(flavour_set.flavours())
    publishing_actions = [
        glci.model.PublishingAction(action.strip()) for action in publishing_actions.split(',')
    ]

    if glci.model.PublishingAction.BUILD_ONLY in publishing_actions:
        print(
            f'publishing action {glci.model.PublishingAction.BUILD_ONLY=} specified - exiting now'
        )
        sys.exit(0)

    find_releases = glci.util.preconfigured(
      func=glci.util.find_releases,
      cicd_cfg=cicd_cfg,
    )

    releases = tuple(
      find_releases(
        flavour_set=flavour_set,
        build_committish=committish,
        version=version,
        gardenlinux_epoch=int(gardenlinux_epoch),
        prefix=glci.model.ReleaseManifest.manifest_key_prefix,
      )
    )

    # ensure all previous tasks really were successful
    is_complete = len(releases) == len(flavours)
    if not is_complete:
        print('release was not complete - will not promote (this indicates a bug!)')
        sys.exit(1)  # do not signal an error

    print(publishing_actions)

    # if this line is reached, the release has been complete
    # now create and publish manifest-set

    upload_release_manifest_set = glci.util.preconfigured(
        func=glci.util.upload_release_manifest_set,
        cicd_cfg=cicd_cfg,
    )

    manifest_set = glci.model.ReleaseManifestSet(
        manifests=releases,
        flavour_set_name=flavour_set.name,
    )

    manifest_path = os.path.join(
        glci.model.ReleaseManifestSet.release_manifest_set_prefix,
        build_type.value,
        glci.util.release_set_manifest_name(
            build_committish=committish,
            gardenlinux_epoch=gardenlinux_epoch,
            version=version,
            flavourset_name=flavour_set.name,
            build_type=build_type,
        ),
    )

    upload_release_manifest_set(
        key=manifest_path,
        manifest_set=manifest_set,
    )

    print(f'uploaded manifest-set: {manifest_path=}')
