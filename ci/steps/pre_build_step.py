import sys

import glci.model
import glci.util
import glci.s3


def pre_build_step(
    cicd_cfg_name: str,
    modifiers: str,
    committish: str,
    version: str,
    gardenlinux_epoch: str,
    architecture: str,
    platform: str,
    publishing_actions: str,
):
    publishing_actions = [
        glci.model.PublishingAction(action.strip()) for action in publishing_actions.split(',')
    ]
    if glci.model.PublishingAction.BUILD_ONLY in publishing_actions:
        print(
            f'publishing action {glci.model.PublishingAction.BUILD_ONLY=} specified - exiting now'
        )
        sys.exit(0)

    cicd_cfg = glci.util.cicd_cfg(cfg_name=cicd_cfg_name)
    s3_client = glci.s3.s3_client(cicd_cfg)
    s3_bucket_name = cicd_cfg.build.s3_bucket_name

    modifiers = tuple([m for m in modifiers.split(',') if m])

    release_identifier = glci.model.ReleaseIdentifier(
      build_committish=committish,
      version=version,
      gardenlinux_epoch=int(gardenlinux_epoch),
      architecture=glci.model.Architecture(architecture),
      platform=platform,
      modifiers=modifiers,
    )

    if glci.util.find_release(
      s3_client=s3_client,
      bucket_name=s3_bucket_name,
      release_identifier=release_identifier,
      prefix=glci.model.ReleaseManifest.manifest_key_prefix,
    ):
      with open('/workspace/skip_build', 'w') as f:
          f.write('skip build (already done)')
      print('build already done - telling next step to skip (/workspace/skip_build touched)')
    else:
      print('no matching build results found - will perform build')
