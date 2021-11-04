import os

import build_kaniko as builder


def build_base_image(
    build_image: str,
    gardenlinux_build_deb_image: str,
    repo_dir: str,
    oci_path: str,
    version_label: str,
):
    # check if build is configured to use an existing (older) base-image
    # if yes skip building base images otherwise build base images for commit
    targeted_build_deb_image = f'{oci_path}/gardenlinux-build-deb:{version_label}'
    targeted_build_image = f'{oci_path}/gardenlinux-build-image:{version_label}'

    if gardenlinux_build_deb_image != targeted_build_deb_image and build_image != targeted_build_image:
        print(f'Build will use (older) base images {gardenlinux_build_deb_image}, {build_image}'
            ' skip step.')
        return

    dockerfile_relpath = os.path.join(repo_dir, "docker", "build-image", "Dockerfile")
    print(f'repo_dir is: {repo_dir}')

    docker_dirs = ['build', 'build-deb', 'build-image']

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
            additional_tags=['latest'],
            build_args=[f'build_base_image={build_base_image}']
        )
