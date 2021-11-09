import sys

import glci.model
import glci.util
import glci.s3


def _write_not_build_marker_file(reason: str):
    with open('/workspace/skip_build', 'w') as f:
        f.write('skip build (already done or build not in build_targets)')
    print(f'build skipped: {reason} - telling next step to skip (/workspace/skip_build touched)')


def pre_build_step(
    cicd_cfg_name: str,
    modifiers: str,
    committish: str,
    version: str,
    gardenlinux_epoch: str,
    architecture: str,
    platform: str,
    build_targets: str,
):
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)
    if not glci.model.BuildTarget.BUILD in build_target_set:
        _write_not_build_marker_file('build not in build-targets')
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
        _write_not_build_marker_file('already done')
    else:
        print('no matching build results found - will perform build')
