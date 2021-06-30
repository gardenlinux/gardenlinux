import sys

import glci.model
import glci.util
import promote

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
    if glci.model.PublishingAction.RELEASE not in publishing_actions:
        print(
            f'publishing action {glci.model.PublishingAction.RELEASE=} not specified - exiting now'
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
    # XXX now create and publish manifest-set
    print('XXX should not publish manifest-set (not implemented, yet)')
