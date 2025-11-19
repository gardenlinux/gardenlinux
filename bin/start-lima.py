#!/usr/bin/env python3

import argparse
import sys
import yaml
from urllib.request import urlopen
import subprocess
import json
from pathlib import Path
import platform
import tempfile

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
    
    # Get Latest nightly version
    command = [glrd_path, "--latest", "--type", "nightly", "--output-format", "json"]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    latest_nightly_version = str(json.loads(result.stdout)["releases"][0]["version"]["major"]) + "." + \
        str(json.loads(result.stdout)["releases"][0]["version"]["minor"]) + "." + \
        str(json.loads(result.stdout)["releases"][0]["version"]["patch"])

    if version == "nightly":
        command = [glrd_path, "--latest", "--type", version, "--output-format", "json"]
    elif version.split(".")[0] == "1877" or version.split(".")[0] == "1592":
        print("Error: 1877 or 1592 GL Version does not support lima platform. Please verify")
        sys.exit(1)
    elif version <= latest_nightly_version:
        command = [glrd_path, "--type", "nightly", "--version", version, "--output-format", "json"]
    elif version == "latest": #TODO: Update once major release supports lima platform
        print("Error: 1877 or 1592 GL Version does not support lima platform. Please verify")
        sys.exit(1)
        #command = [glrd_path, "--latest", "--output-format", "json"]
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
    yaml_config_data["images"][0]["location"] = image_path
    yaml_config_data["images"][0]["arch"] = "x86_64" if arch == "amd64" else "aarch64"

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=True) as tmp:
        with open(tmp.name, "w") as f:
            yaml.dump(yaml_config_data, f, default_flow_style=False, sort_keys=False)
        yaml_file = tmp.name
        subprocess.run(["limactl", "start", yaml_file, "--name", name], check=True)

def main():
    parser = argparse.ArgumentParser(
        description="Start a Garden Linux VM using Lima"
    )

    parser.add_argument(
        "--version",
        default='nightly',
        help="By default starts latest nightly build. \
            Provide specific version for older nightly builds. Default:nightly"
    )

    parser.add_argument(
        "--arch",
        default=platform.machine(),
        help="Optional: Provide architecture if specific architecture is needed. Default: Platform architecture"
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
