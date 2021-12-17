import glob
import os

import build_kaniko as builder
import glci.model
import version


def build_base_image(
    build_image: str,
    gardenlinux_build_deb_image: str,
    repo_dir: str,
    oci_path: str,
    version_label: str,
    build_targets: str,
):
    additional_tags = ['latest']
    build_target_set = glci.model.BuildTarget.set_from_str(build_targets)

    # check if build is configured to use an existing (older) base-image
    # if yes skip building base images otherwise build base images for commit
    targeted_build_deb_image = f'{oci_path}/gardenlinux-build-deb:{version_label}'
    targeted_build_image = f'{oci_path}/gardenlinux-build-image:{version_label}'

    if (gardenlinux_build_deb_image != targeted_build_deb_image and
        build_image != targeted_build_image):
        print(f'Build will use (older) base images {gardenlinux_build_deb_image}, {build_image}'
            ' skip step.')
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

    dockerfile_relpath = os.path.join(repo_dir, "docker", "build-image", "Dockerfile")
    print(f'repo_dir is: {repo_dir}')

    docker_dirs = ['build', 'build-deb', 'build-image']

    go_files = glob.glob(os.path.join(repo_dir, "bin", '*.go'), recursive=False)
    for f in go_files:
        f_name = os.path.basename(f)
        dst = os.path.join(repo_dir, "docker", 'build-image', f_name)
        os.symlink(f, dst)

    for docker_dir in docker_dirs:
        dockerfile_relpath = os.path.join(repo_dir, "docker", docker_dir, "Dockerfile")
        print(f'---Building now {dockerfile_relpath}')

        if docker_dir == 'build-deb':
            build_base_image = f'{oci_path}/gardenlinux-build:{version_label}'
        else:
            build_base_image = 'debian:testing-slim'

        context_dir = os.path.join(repo_dir, "docker", docker_dir)
        print(f'---Using base image {build_base_image}')
        builder.build_and_push_kaniko(
            dockerfile_path=dockerfile_relpath,
            context_dir=context_dir,
            image_push_path=f'{oci_path}/gardenlinux-{docker_dir}',
            image_tag=version_label,
            additional_tags=additional_tags,
            build_args=[f'build_base_image={build_base_image}']
        )
