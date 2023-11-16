#!/usr/bin/env python3
import os
import tempfile
import json

from bs4 import BeautifulSoup
from urllib.request import urlopen, urlretrieve
from datetime import datetime, timedelta

SHA_SUMS = "SHA512SUMS"

DEBIAN_TESTING_BASE_URL = 'https://cloud.debian.org/images/cloud/trixie/daily'

"""
This script is here to update lima-dev-env.yaml
It will check for things that can be updated such as debian images.
Please test if the updated images work before merging changes created by this script.

This script is supposed to not rely on any external dependencies (except for BeautifulSoup)
"""

lima_manifest_template = """vmType: qemu
os: Linux
memory: 8GiB
ssh:
  loadDotSSHPubKeys: true
containerd:
  system: false
  user: false

images:
  - location: "__AMD64_IMAGE_URL__"
    arch: "x86_64"
    digest: "sha512:__AMD64_IMAGE_CSUM__"
  - location: "__ARM64_IMAGE_URL__"
    arch: "aarch64"
    digest: "sha512:__ARM64_IMAGE_CSUM__"

provision:
  - mode: system
    script: |
      #!/bin/bash
      set -eux -o pipefail
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      command -v podman >/dev/null 2>&1 && exit 0
      apt-get -y install podman git curl qemu-system-x86 qemu-system-arm qemu-efi-aarch64 qemu-user-static python3-bs4
      # Install github cli gh, pin to version to allow checksum compare
      # On update, update both GH_CSUM and the download url
      ARCH=$(dpkg --print-architecture)
      declare -A GH_CSUM
      GH_CSUM=( ["amd64"]="__GH_AMD64_CSUM__" ["arm64"]="__GH_ARM64_CSUM__")
      curl -fsSL https://github.com/cli/cli/releases/download/v__GH_VERSION__/gh___GH_VERSION___linux_$ARCH.deb --output gh.deb
      calculated_checksum=$(sha256sum gh.deb | awk '{ print $1 }')
      if [ ${GH_CSUM[$ARCH]} == "$calculated_checksum" ]; then
          apt install -y ./gh.deb
          rm gh.deb
      else
          echo "Checksums do not match"
          exit 1
      fi
  - mode: user
    script: |
      #!/bin/bash
      set -eux -o pipefail
      systemctl --user enable --now podman.socket

      if [ ! -d ~/gardenlinux ]
      then
        git clone https://github.com/gardenlinux/gardenlinux ~/gardenlinux
      else
        echo Local checkout of Garden Linux already exists
      fi
"""


def link_without_trailing_slash(link: str):
    return link[:-1]


def deduplicate_list(debian_image_links_with_duplicates):
    return list(set(debian_image_links_with_duplicates))


def get_current_debian_images():
    today = datetime.today().strftime('%Y%m%d')
    print(today)

    yesterday = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    print(yesterday)

    debian_image_links_with_duplicates = []

    with urlopen(DEBIAN_TESTING_BASE_URL) as response:
        soup = BeautifulSoup(response, 'html.parser')
        all_links = soup.find_all('a')
        for anchor in all_links:
            href = anchor.get('href', '/')
            if today in href:
                print(href)
                debian_image_links_with_duplicates.append(href)

        # Because we can't be sure that there is an image for today, also try getting one from yesterday
        if len(debian_image_links_with_duplicates) == 0:
            for anchor in all_links:
                href = anchor.get('href', '/')
                if yesterday in href:
                    print(href)
                    debian_image_links_with_duplicates.append(href)

    debian_image_links = deduplicate_list(debian_image_links_with_duplicates)

    if len(debian_image_links) == 1:
        debian_testing_version = link_without_trailing_slash(debian_image_links[0])

        amd_url = f"{DEBIAN_TESTING_BASE_URL}/{debian_testing_version}/debian-13-genericcloud-amd64-daily-{debian_testing_version}.qcow2"
        arm_url = f"{DEBIAN_TESTING_BASE_URL}/{debian_testing_version}/debian-13-genericcloud-arm64-daily-{debian_testing_version}.qcow2"

        temp_sha_sums_file = f"{tempfile.gettempdir()}/{SHA_SUMS}"
        urlretrieve(f"{DEBIAN_TESTING_BASE_URL}/{debian_testing_version}/{SHA_SUMS}", temp_sha_sums_file)
        amd_sum = ""
        arm_sum = ""
        with open(temp_sha_sums_file) as sums:
            for line in sums:
                if f"debian-13-genericcloud-amd64-daily-{debian_testing_version}.qcow2" in line:
                    amd_sum = line.split("  ")[0]
                if f"debian-13-genericcloud-arm64-daily-{debian_testing_version}.qcow2" in line:
                    arm_sum = line.split("  ")[0]

        os.remove(temp_sha_sums_file)

        print(amd_sum)
        print(arm_sum)

        return dict(
            amd_url = amd_url,
            amd_sum = amd_sum,
            arm_url = arm_url,
            arm_sum = arm_sum
        )
    else:
        raise f"Expected exactly one link in {debian_image_links}"


def tag_without_leading_v(tag: str):
    return tag[1:]


def get_current_gh_cli():
  temp_gh_cli_releases_file = f"{tempfile.gettempdir()}/gh.json"
  temp_gh_cli_csum_file = f"{tempfile.gettempdir()}/gh-csum.txt"
  version = ""
  amd_sum = ""
  arm_sum = ""
  urlretrieve("https://api.github.com/repos/cli/cli/releases/latest", temp_gh_cli_releases_file)
  with open (temp_gh_cli_releases_file) as f:
    releases = json.loads(f.read())
    version = tag_without_leading_v(releases["tag_name"])
    print(f"GH Cli version {version}")
    urlretrieve(f"https://github.com/cli/cli/releases/download/v{version}/gh_{version}_checksums.txt", temp_gh_cli_csum_file)
    with open(temp_gh_cli_csum_file) as ff:
        for line in ff:
          if "linux_arm64.deb" in line:
              arm_sum = line.split("  ")[0]
          if "linux_amd64.deb" in line:
              amd_sum = line.split("  ")[0]
    os.remove(temp_gh_cli_csum_file)
  os.remove(temp_gh_cli_releases_file)
  return dict(
      version = version,
      amd_sum = amd_sum,
      arm_sum = arm_sum
  )


def main():
    current_images = get_current_debian_images()
    current_gh_cli = get_current_gh_cli()

    lima_manifest = lima_manifest_template \
        .replace("__AMD64_IMAGE_URL__", current_images['amd_url']) \
        .replace("__AMD64_IMAGE_CSUM__", current_images['amd_sum']) \
        .replace("__ARM64_IMAGE_URL__", current_images['arm_url']) \
        .replace("__ARM64_IMAGE_CSUM__", current_images['arm_sum']) \
        .replace("__GH_AMD64_CSUM__", current_gh_cli['amd_sum']) \
        .replace("__GH_ARM64_CSUM__", current_gh_cli['arm_sum']) \
        .replace("__GH_VERSION__", current_gh_cli['version'])

    with open("hack/lima-dev-env/gl-dev.yaml", "w+") as file:
        file.write(lima_manifest)


if __name__ == '__main__':
    main()
