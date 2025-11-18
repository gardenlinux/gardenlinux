#!/usr/bin/env python3

import argparse
import sys
import yaml
from urllib.request import urlopen
import subprocess
import json
from pathlib import Path
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
    script_dir = Path(__file__).resolve().parent
    # Construct the path to the glrd script
    glrd_path = str(script_dir / "glrd")

    gl_minor_version_supporting_lima = [8, 16]
    
    # Get Latest version supported by GL
    command = [glrd_path, "--latest", "--output-format", "json"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    latest_gl_major_version = json.loads(result.stdout)["releases"][0]["version"]["major"]
    latest_gl_minor_version = json.loads(result.stdout)["releases"][0]["version"]["minor"]

    # Get Latest minor version for 1592
    command = [glrd_path, "--latest", "--type", "minor", "--version", "1592", "--output-format", "json"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    latest_gl1592_minor_version = json.loads(result.stdout)["releases"][0]["version"]["minor"]
    
    # Get Latest nightly version
    command = [glrd_path, "--latest", "--type", "nightly", "--output-format", "json"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    latest_nightly_version = str(json.loads(result.stdout)["releases"][0]["version"]["major"]) + "." + str(json.loads(result.stdout)["releases"][0]["version"]["minor"])

    if version == "nightly":
        command = [glrd_path, "--latest", "--type", version, "--output-format", "json"]
    elif version == "latest":
        command = [glrd_path, "--latest", "--output-format", "json"]
    elif (int(version.split(".")[0]) == latest_gl_major_version and int(version.split(".")[1]) > latest_gl_minor_version) or \
         (version.split(".")[0] == "1592" and int(version.split(".")[1]) > latest_gl1592_minor_version):
        print("Error: Version not supported. Please verify")
        sys.exit(1)
    elif (int(version.split(".")[0]) == latest_gl_major_version and int(version.split(".")[1]) >= gl_minor_version_supporting_lima[0]) or \
         (version.split(".")[0] == "1592" and int(version.split(".")[1]) >= gl_minor_version_supporting_lima[1]):
        command = [glrd_path, "--version", version, "--output-format", "json"]
    elif (int(version.split(".")[0]) == latest_gl_major_version and int(version.split(".")[1]) < gl_minor_version_supporting_lima[0]) or \
         (version.split(".")[0] == "1592" and int(version.split(".")[1]) < gl_minor_version_supporting_lima[1]):
        print("Error: Provided version does not support lima image. Please verify. Supported version >= 1877.8 or >= 1592.16")
        sys.exit(1)
    elif version < latest_nightly_version:
        command = [glrd_path, "--type", "nightly", "--version", version, "--output-format", "json"]
    else:
        print("Error: Provided version is not correct. Please verify")
        sys.exit(1)

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        image_name = f"lima-{arch}"
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

def generate_yaml(image_path, name, arch):
    yaml_file = "gardenlinux.yaml"

    yaml_config_data["images"][0]["location"] = image_path
    yaml_config_data["images"][0]["arch"] = "x86_64" if arch == "amd64" else "aarch64"

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
        default='latest',
        help="By default starts latest release version. \
            Provide specific version or 'nightly' to start nightly build. Default:latest"
    )

    parser.add_argument(
        "--arch",
        default='amd64',
        help="Provide architecture amd64 or arm64. Default:amd64"
    )

    parser.add_argument(
        "--name",
        default='gardenlinux',
        help="Provide name of the VM. Default:gardenlinux"
    )

    args = parser.parse_args()
    
    print(f"Starting Garden Linux VM with version {args.version}")
    image_path = get_image_path(args.version, args.arch)
    generate_yaml(image_path, args.name, args.arch)


if __name__ == "__main__":
    main()
