#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
from pathlib import Path
import sys

def get_git_root():
    """Get the root directory of the current Git repository."""
    try:
        root_dir = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip()
        return Path(root_dir)
    except subprocess.CalledProcessError:
        print("Error: Not a git repository or unable to determine root directory.")
        sys.exit(1)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate OpenTofu variable files based on provided test prefix, platforms, archs, and flavors."
    )
    
    parser.add_argument(
        'test_prefix', 
        type=str, 
        help="The test prefix to include in the variable files."
    )
    parser.add_argument(
        '--flavors', 
        type=str, 
        default="ali-gardener_prod-amd64,aws-gardener_prod-amd64,azure-gardener_prod-amd64,gcp-gardener_prod-amd64",
        help="Comma-separated list of flavors (default: 'ali-gardener_prod-amd64,aws-gardener_prod-amd64,azure-gardener_prod-amd64,gcp-gardener_prod-amd64')."
    )
    parser.add_argument(
        '--root-dir', 
        type=str, 
        default=None, 
        help="Root directory for the variable files. Defaults to the current Git repository's root."
    )
    parser.add_argument(
        '--image-path', 
        type=str, 
        default=None, 
        help="Base path for image files."
    )
    parser.add_argument(
        '--cname', 
        type=str, 
        default=None, 
        help="Basename of image file, e.g. 'gcp-gardener_prod-arm64-1592.2-76203a30'."
    )
    
    return parser.parse_args()


def create_tfvars_file(args, flavor, root_dir):
    """Create .tfvars files for each combination of platform, architecture, and flavor."""
    var_file = Path(root_dir) / f"tests/platformSetup/tofu/variables.{flavor}.tfvars"

    with open(var_file, 'w') as f:
        f.write(f'test_prefix = "{args.test_prefix}"\n')

        if args.image_path:
            f.write(f'image_path= "{args.image_path}"\n')

        azure_subscription_id = os.getenv('azure_subscription_id')
        if not azure_subscription_id:
            sys.exit("Error: 'azure_subscription_id' environment variable is required for Azure.")
        f.write(f'azure_subscription_id = "{azure_subscription_id}"\n')

        gcp_project = os.getenv('gcp_project')
        if not gcp_project:
            sys.exit("Error: 'gcp_project' environment variable is required for GCP.")
        f.write(f'gcp_project_id = "{gcp_project}"\n')

        parts = flavor.split('-')
        # Extract platform (first part) and architecture (last part)
        platform = parts[0]
        arch = parts[-1]
        if arch not in {"amd64", "arm64"}:
            print(f"Error: Unsupported architecture '{arch}'. Valid options are 'amd64' or 'arm64'.", file=sys.stderr)
            sys.exit(1)

        # All middle parts are features, split them by '_' to expand multi-part features
        features_string = "-".join(parts[1:-1])
        raw_features = features_string.replace("_", "-_")  # Rejoin middle parts to handle mixed cases
        feature_list = [feature for feature in raw_features.split("-")]

        features = json.dumps(feature_list)  # Make sure to have double quotes

        instance_types = {
            "ali": {"amd64": "ecs.t6-c1m2.large", "arm64": "ecs.g8y.small"},
            "aws": {"amd64": "m5.large", "arm64": "m6g.medium"},
            "azure": {"amd64": "Standard_D4_v4", "arm64": "Standard_D4ps_v5"},
            "gcp": {"amd64": "n1-standard-2", "arm64": "t2a-standard-2"},
        }

        if args.cname:
            cname = args.cname
        else:
            cname = f'{platform}-{features_string}-{arch}-today-local'

        image_files = {
            "ali": f'{cname}.qcow2',
            "aws": f'{cname}.raw',
            "azure": f'{cname}.vhd',
            "gcp": f'{cname}.gcpimage.tar.gz',
        }

        flavor_item = {
            "name": flavor,
            "platform": platform,
            "features": json.loads(features),
            "arch": arch,
            "instance_type":instance_types[platform][arch],
            "image_file": image_files[platform]
        }

        flavors_list = [flavor_item]
        formatted_flavors = json.dumps(flavors_list, indent=2)

        f.write(f'flavors = {formatted_flavors}\n')        


    print(f"Created: {var_file}")


def main():
    args = parse_arguments()

    # Split comma-separated values
    input_flavors = args.flavors.split(',')
    root_dir = Path(args.root_dir) if args.root_dir else get_git_root()

    for input_flavor in input_flavors:
        create_tfvars_file(args, input_flavor, root_dir)

if __name__ == "__main__":
    main()

