#!/usr/bin/env python3

# This script generates a YAML manifest for using Garden Linux as a guest with lima-vm.
# It outputs only the YAML to stdout, allowing piping directly into limactl to create a new guest.
# The script is necessary because Garden Linux image URLs are not straightforward to construct.

import argparse
import sys
import yaml
import subprocess
import json
from pathlib import Path

# Build config as a Python dict
yaml_config_data = {
    "os": "Linux",
    "images": [],
    "containerd": {
        "system": False, 
        "user": False
    },
    "mountTypesUnsupported": ["9p"],
    "ssh": {
        "loadDotSSHPubKeys": True, 
        "forwardAgent": True
    },
    "mounts": [{"location": "~", "writable": False}],
}

def construct_command(version, allow_nightly):
    script_dir = Path(__file__).resolve().parent
    # Construct the path to the glrd script
    glrd_path = str(script_dir / "glrd")

    if version == "nightly":
        command = [glrd_path, "--latest", "--type", "nightly", "--output-format", "json"]
    elif version == "latest":
        command = [glrd_path, "--latest", "--type", "minor", "--output-format", "json"]
    else:
        image_type = "nightly" if allow_nightly else "minor"
        command = [glrd_path, "--latest", "--type", image_type, "--version", version, "--output-format", "json"]

    return command

def get_image_path(command, version):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}", file=sys.stderr)
        raise

    image_paths = {
        'x86_64': '',
        'aarch64': ''
    }

    for arch in ['amd64', 'arm64']:
        output = json.loads(result.stdout)
        image_name = f"lima-{arch}"
        if not output["releases"] == []:
            try:
                lima_image_for_arch = output["releases"][0]["flavors"][image_name]
            except KeyError:
                print(f"The specified version {version} has no lima image available. Try a newer version.", file=sys.stderr)
                exit(1)

            if not lima_image_for_arch:
                print(f"Error: No Lima image found for the specified version.", file=sys.stderr)
                sys.exit(1)
        else:
            print("Error: No releases found for the specified version.", file=sys.stderr)
            sys.exit(1)

        if arch == 'amd64':
            image_paths['x86_64'] = lima_image_for_arch["image"]
        else:
            image_paths['aarch64'] = lima_image_for_arch["image"]

    return image_paths


def generate_yaml(image_paths):
    yaml_config_data["images"].append({'location': image_paths['x86_64'], 'arch': 'x86_64'})
    yaml_config_data["images"].append({'location': image_paths['aarch64'], 'arch': 'aarch64'})

    print(yaml.dump(yaml_config_data, default_flow_style=False, sort_keys=False))

def main():
    parser = argparse.ArgumentParser(
        description="Generate lima-vm manifests for use with Garden Linux guests"
    )

    # FIXME: Change the default value to 'latest' prior to our next major release
    # Using nightly as the default value temporarily for easier usage because no released version is built with the lima feature.
    # 'latest' should be the default value starting with the next major version.
    parser.add_argument(
        "--nightly",
        default='latest',
        help="Provide a specific Garden Linux version, or use 'latest' or 'nightly'."
    )

    parser.add_argument(
        '--allow-nightly',
        action='store_true',
        help="Query nightly versions, needed for getting a specific nightly version of Garden Linux."
        )

    args = parser.parse_args()

    command = construct_command(args.version, args.allow_nightly)
    image_paths = get_image_path(command, args.version)
    generate_yaml(image_paths)


if __name__ == "__main__":
    main()
