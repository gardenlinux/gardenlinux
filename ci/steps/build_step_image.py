import glob
import os
import logging

import build_kaniko as builder
import glci.model
import version

logger = logging.getLogger(__name__)


def build_step_image(
    repo_dir: str,
    oci_path: str,
    version_label: str,
    build_targets: str,
):
    additional_tags = ['latest']
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    if not glci.model.BuildTarget.BASE_BUILD in build_target_set:
        print(f'Build target {glci.model.BuildTarget.BASE_BUILD.value} not set: skip base image'
            ' build')
        return

    # if we are in a release and have a .x version with x>0 do not build base image
    # use the existing one.
    parsed_version = version.parse_to_semver(version_label)
    if parsed_version.minor > 0:
        print(f'Skip building base images for versions with minor > 0: {version_label}')

    if glci.model.BuildTarget.FREEZE_VERSION in build_target_set and parsed_version.minor == 0:
        tag = f'rel-{parsed_version.major}'
        print(f'Set additional tag for later minor releases: {tag}')
        additional_tags.append(tag)

    dockerfile_relpath = os.path.join(repo_dir, 'ci', 'images', 'step_image', 'Dockerfile')
    ctx = os.path.join(repo_dir, 'ci', 'images', 'step_image')
    logger.info(f'repo_dir is: {repo_dir}')

    builder.build_and_push_kaniko(
        dockerfile_path=dockerfile_relpath,
        context_dir=ctx,
        image_push_path=f'{oci_path}/gardenlinux-step-image',
        image_tag=version_label,
        additional_tags=additional_tags,
    )
