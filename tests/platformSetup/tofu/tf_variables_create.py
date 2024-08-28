#!/usr/bin/env python3
import argparse
import json
import os
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
        '--platforms', 
        type=str, 
        # required=True, 
        default="ali,aws,azure,gcp",
        help="Comma-separated list of platforms (e.g., ali,aws,azure,gcp)."
    )
    parser.add_argument(
        '--archs', 
        type=str, 
        # required=True, 
        default="amd64,arm64",
        help="Comma-separated list of archs (e.g., amd64,arm64)."
    )
    parser.add_argument(
        '--flavors', 
        type=str, 
        default="default,trustedboot,trustedboot_tpm2",
        help="Comma-separated list of flavors (default: 'default,trustedboot,trustedboot_tpm2')."
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
    parser.add_argument(
        '--image-file-ali', 
        type=str, 
        default=None, 
        help="Specific ALI image file."
    )
    parser.add_argument(
        '--image-file-aws', 
        type=str, 
        default=None, 
        help="Specific AWS image file."
    )
    parser.add_argument(
        '--image-file-azure', 
        type=str, 
        default=None, 
        help="Specific Azure image file."
    )
    parser.add_argument(
        '--image-file-gcp', 
        type=str, 
        default=None, 
        help="Specific GCP image file."
    )
    
    return parser.parse_args()


def write_platform_specific_config(f, args, platform, arch, flavor):
    """Write platform-specific configuration to the file."""
    instance_types = {
        "ali": {"amd64": "ecs.t6-c1m2.large", "arm64": "ecs.g8y.small"},
        "aws": {"amd64": "m5.large", "arm64": "m6g.medium"},
        "azure": {"amd64": "Standard_D4_v4", "arm64": "Standard_D4ps_v5"},
        "gcp": {"amd64": "n1-standard-2", "arm64": "t2a-standard-2"},
    }

    if args.image_path:
        f.write(f'image_path= "{args.image_path}"\n')

    if platform == "ali":
        # f.write('ali_enabled = true\n')
        f.write(f'ali_instance_type = "{instance_types["ali"].get(arch)}"\n')
        if args.image_file_ali:
            f.write(f'ali_image_file = "{args.image_file_ali}"\n')
        elif args.cname:
            f.write(f'ali_image_file = "{args.cname}.qcow2"\n')
        else:
           image_file = f'ali-gardener_prod-{arch}-today-local.qcow2'
           f.write(f'ali_image_file = "{image_file}"\n')

    if platform == "aws":
        # f.write('aws_enabled = true\n')
        f.write(f'aws_instance_type = "{instance_types["aws"].get(arch)}"\n')
        if args.image_file_aws:
            f.write(f'aws_image_file = "{args.image_file_aws}"\n')
        elif args.cname:
            f.write(f'aws_image_file = "{args.cname}.raw"\n')
        else:
           image_file = f'aws-gardener_prod-{arch}-today-local.raw'
           f.write(f'aws_image_file = "{image_file}"\n')

    elif platform == "azure":
        # f.write('azure_enabled = true\n')
        f.write(f'azure_instance_type = "{instance_types["azure"].get(arch)}"\n')
        if args.image_file_azure:
            f.write(f'azure_image_file = "{args.image_file_azure}"\n')
        elif args.cname:
            f.write(f'azure_image_file = "{args.cname}.vhd"\n')
        else:
           image_file = f'azure-gardener_prod-{arch}-today-local.vhd'
           f.write(f'azure_image_file = "{image_file}"\n')

    elif platform == "gcp":
        # f.write('gcp_enabled = true\n')
        f.write(f'gcp_instance_type = "{instance_types["gcp"].get(arch)}"\n')
        if args.image_file_gcp:
            f.write(f'gcp_image_file = "{args.image_file_gcp}"\n')
        elif args.cname:
            f.write(f'gcp_image_file = "{args.cname}.gcpimage.tar.gz"\n')
        else:
           image_file = f'gcp-gardener_prod-{arch}-today-local.gcpimage.tar.gz'
           f.write(f'gcp_image_file = "{image_file}"\n')

    # is needed to query tf API
    azure_subscription_id = os.getenv('azure_subscription_id')
    if not azure_subscription_id:
        sys.exit("Error: 'azure_subscription_id' environment variable is required for Azure.")
    f.write(f'azure_subscription_id = "{azure_subscription_id}"\n')

    gcp_project = os.getenv('gcp_project')
    if not gcp_project:
        sys.exit("Error: 'gcp_project' environment variable is required for GCP.")
    f.write(f'gcp_project_id = "{gcp_project}"\n')


def create_tfvars_files(args, platforms, archs, flavors, root_dir):
    """Create .tfvars files for each combination of platform, architecture, and flavor."""
    for platform in platforms:
        for arch in archs:
            for flavor in flavors:
                var_file = Path(root_dir) / f"tests/platformSetup/tofu/variables.{platform}.{arch}.{flavor}.tfvars"

    with open(var_file, 'w') as f:
        f.write(f'test_prefix = "{args.test_prefix}"\n')
        f.write(f'platforms = ["{platform}"]\n')
        f.write(f'archs = ["{arch}"]\n')
        f.write(f'flavor = "{flavor}"\n')
        if features:
            f.write(f'features = {features}\n')
        else:
            f.write(f'features = []\n')
        write_platform_specific_config(f, args, platform, arch, flavor)

                print(f"Created: {var_file}")


def main():
    args = parse_arguments()

    # Split comma-separated values
    platforms = args.platforms.split(',')
    archs = args.archs.split(',')
    flavors = args.flavors.split(',')
    root_dir = Path(args.root_dir) if args.root_dir else get_git_root()

    for flavor in flavors:
        platform = flavor.split('-')[0]
        arch = flavor.split('-')[-1]

        # Extract all parts after the platform and before the architecture
        parts = flavor.split('-')[1:-1]

        # Process features, removing specific prefixes and handling separators
        features = []
        for part in parts:
            part = re.sub('^(dev|gardener_prod)', '', part)  # Remove specific prefixes
            raw_features = part.replace("_", "-_").split("-")  # Handle mixed separators
            for feature in raw_features:
                if feature:  # Ignore empty strings
                    features.append(feature)
        features = json.dumps(features)  # Make sure to have double quotes
        
        print(f"Platform: {platform}")
        print(f"Architecture: {arch}")
        print(f"Flavor: {flavor}")        
        print(f"Features: {features}")        
        create_tfvars_file(args, platform, flavor, features, arch, root_dir)

if __name__ == "__main__":
    main()

