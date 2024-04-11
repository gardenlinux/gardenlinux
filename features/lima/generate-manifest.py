import argparse
import hashlib
from pathlib import Path

# inputs:
# - cname_base, sample value: kvm_curl-lima
# - version: either today or like 1443.3
# - commit id, sample value: a8fd0355

# this script needs python >= 3.12

template = """# Lima file for Garden Linux
# See https://gardenlinux.io/ for infos on Garden Linux
# See https://lima-vm.io/ for infos on Lima

# To create a new vm:
#  limactl create --name=gardenlinux-__VERSION__ https://images.gardenlinux.io/__YAML_NAME__

vmType: qemu
os: Linux
images:
  - location: "https://images.gardenlinux.io/__DISK_IMAGE_NAME_AMD__"
    arch: "x86_64"
    digest: "sha256:__SHA_AMD__"

  - location: "https://images.gardenlinux.io/__DISK_IMAGE_NAME_ARM__"
    arch: "aarch64"
    digest: "sha256:__SHA_ARM__"

containerd:
  system: false
  user: false
"""


def disk_image_name(cname_base, arch, gardenlinux_version, commit_id):
    return f'{cname_base}-{arch}-{gardenlinux_version}-{commit_id}.qcow2'

def output_file_name(cname_base, gardenlinux_version):
    return f'{cname_base}-{gardenlinux_version}.yaml'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                        prog='LimaManifestGenerator',
                        description='Generates a Lima-VM yaml manifest for Garden Linux')

    parser.add_argument('--cname_base')
    parser.add_argument('--gardenlinux_version')
    parser.add_argument('--commit_id')
    parser.add_argument('--build_dir', default='.build')

    args = parser.parse_args()

    cname_base = args.cname_base
    gardenlinux_version = args.gardenlinux_version
    commit_id_short = args.commit_id[0:8]
    build_dir = Path(args.build_dir)

    disk_image_name_amd64 = disk_image_name(cname_base, 'amd64', gardenlinux_version, commit_id_short)
    disk_image_name_arm64 = disk_image_name(cname_base, 'arm64', gardenlinux_version, commit_id_short)

    sha_amd64 = ""
    sha_arm64 = ""
    with open(build_dir / disk_image_name_amd64, 'rb', buffering=0) as f:
        sha_amd64 = hashlib.file_digest(f, 'sha256').hexdigest()

    with open(build_dir / disk_image_name_arm64, 'rb', buffering=0) as f:
        sha_arm64 = hashlib.file_digest(f, 'sha256').hexdigest()

    yaml_name = output_file_name(cname_base, gardenlinux_version)

    manifest = template\
        .replace("__DISK_IMAGE_NAME_AMD__", disk_image_name_amd64)\
        .replace("__DISK_IMAGE_NAME_ARM__", disk_image_name_arm64)\
        .replace("__SHA_AMD__", sha_amd64)\
        .replace("__SHA_ARM__", sha_arm64)\
        .replace("__YAML_NAME__", yaml_name)\
        .replace("__VERSION__", gardenlinux_version)

    with open(yaml_name, "w+") as file:
        file.write(manifest)
