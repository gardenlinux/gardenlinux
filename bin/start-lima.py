#!/usr/bin/env python3

import argparse
import sys
import yaml
from urllib.request import urlopen
import subprocess
import json
import os

# Build config as a Python dict
yaml_config_data = {
    "os": "Linux",
    "images": [
        {"location": "", "arch": ""}
    ],
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

def get_image_path(version, arch):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    # Construct the path to the glrd script
    glrd_path = os.path.join(script_dir, "glrd")
    if version in ["latest", "nightly"]:
        command = [glrd_path, "--latest", "--type", version, "--output-format", "json"]
    else:
        command = [glrd_path, "--version", version, "--output-format", "json"]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        image_name = f"openstack-gardener_prod-{arch}"
        image_path = output["releases"][0]["flavors"][image_name]["image"]
        return image_path
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e.stderr}")
        raise
    except KeyError as e:
        print(f"Error parsing JSON: Missing key {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        raise

def generate_yaml(image_path, name):
    yaml_file = "gardenlinux.yaml"

    yaml_config_data["images"][0]["location"] = image_path
    yaml_config_data["images"][0]["arch"] = "amd64"

    with open(yaml_file, "w") as f:
        yaml.dump(yaml_config_data, f, default_flow_style=False, sort_keys=False)
    
    subprocess.run(["limactl", "start", yaml_file, "--name", name], check=True)

def main():
    arch = None
    version = None

    parser = argparse.ArgumentParser(
        description="Start Lima image"
    )

    parser.add_argument(
        "--version",
        const=None,
        help="Provide daily to start latest night build, latest to start latest release image \
                or version number to start particular version of GL"
    )

    parser.add_argument(
        "--arch",
        const=None,
        help="Provide architecture amd64 or arm64. Default:amd64"
    )

    parser.add_argument(
        "--name",
        const=None,
        help="Provide name of the VM. Default:gardenlinux"
    )

    args = parser.parse_args()
    if args.arch is None:
        arch = "amd64"
    else:
        arch = args.arch

    if args.name is None:
        name = "gardenlinux"
    else:
        name = args.name
    
    if args.version is None:
        print("Error: Provide version value\n")
        parser.print_help()
        sys.exit(1)
    else:
        version = args.version
        print(f"Starting Lima Image {version}")
        image_path = get_image_path(version, arch)
        generate_yaml(image_path, name)


if __name__ == "__main__":
    main()
