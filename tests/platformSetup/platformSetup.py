#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
import logging
from pathlib import Path
import yaml
import tempfile
import shutil
import uuid
import os.path
import re
from datetime import datetime, timezone
import requests
from glob import glob
from urllib.parse import urlparse

from python_gardenlinux_lib.features.parse_features import get_features
from python_gardenlinux_lib import Git, Version

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(handler)

# Global constants
PROVISIONER_PYTEST_MAP = {
    "qemu": "qemu",
    "tofu": "manual"
}

class PathManager:
    """Manages paths used throughout the application."""
    def __init__(self):
        self.git_root = Git().get_root()
        self.tests_dir = self.git_root / "tests"
        self.config_dir = self.tests_dir / "config"
        self.platform_setup_dir = self.tests_dir / "platformSetup"
        self.tofu_dir = self.platform_setup_dir / "tofu"
        self.uuid_file = self.platform_setup_dir / ".uuid"

        # Ensure directories exist
        self.config_dir.mkdir(exist_ok=True)
        self.platform_setup_dir.mkdir(exist_ok=True)
        self.tofu_dir.mkdir(exist_ok=True)
        # Set up UUID
        self.uuid = self.get_or_create_uuid()
        self.seed = self.uuid.split('-')[0]

    def get_or_create_uuid(self):
        """Get existing UUID from file or create a new one."""
        try:
            if self.uuid_file.exists():
                # Read existing UUID
                with self.uuid_file.open('r') as f:
                    existing_uuid = f.read().strip()
                logger.debug(f"Using existing UUID: {existing_uuid}")
                return existing_uuid
            else:
                # Generate new UUID and save it
                new_uuid = str(uuid.uuid4()).lower()
                with self.uuid_file.open('w') as f:
                    f.write(new_uuid)
                logger.debug(f"Generated new UUID: {new_uuid}")
                return new_uuid
        except Exception as e:
            logger.error(f"Error handling UUID file: {e}")
            sys.exit(1)

class Flavors:
    """Handles parsing and processing of flavor information."""
    def __init__(self, args, paths):
        self.args = args
        self.paths = paths
        self.flavor = args.flavor
        self.provisioner = args.provisioner
        self.platform, self.feature_list, self.image_features, self.arch = self.parse_features()

    def parse_features(self):
        """Parse features from the flavor name."""
        parts = self.flavor.split("-")

        if len(parts) < 3:
            logger.error("Flavor name must be in the format 'platform-features-arch'")
            sys.exit(1)

        platform = parts[0]
        features_image_name = "-".join(parts[1:-1])
        arch = parts[-1]

        if arch not in {"amd64", "arm64"}:
            logger.error(f"Unsupported architecture '{arch}'. Valid options are 'amd64' or 'arm64'.")
            sys.exit(1)

        print(f"features_image_name: {features_image_name}")

        # Create flavor string without architecture
        flavor_without_arch = "-".join(parts[:-1])

        # Use gardenlinux library to resolve features
        features_dir = str(self.paths.git_root)
        feature_string_comma = get_features(flavor_without_arch, features_dir)

        # Convert comma-separated string to list
        feature_list = feature_string_comma.split(",")

        logger.info(f"Flavor: {self.flavor}")
        logger.info(f"Platform: {platform}")
        logger.info(f"Provisioner: {self.provisioner}")
        logger.info(f"Features: {feature_list}")
        logger.info(f"Architecture: {arch}")

        return platform, feature_list, features_image_name, arch

class PytestConfig:
    """Generates pytest configuration files."""
    def __init__(self, args, paths, flavors, script):
        self.args = args
        self.paths = paths
        self.flavors = flavors
        self.script = script

    def generate_pytest_configfile(self, config_data, image_path=None, image_name=None):
        """Generate a pytest configuration file."""
        flavor = self.flavors.flavor
        platform = config_data["platform"]
        provisioner = self.args.provisioner
        provisioner_pytest = PROVISIONER_PYTEST_MAP[provisioner]

        if image_name is None:
            image_name = self.script.get_image_name()

        if provisioner == "qemu":
            config_file = self.paths.config_dir / f"pytest.{provisioner_pytest}.{flavor}.yaml"
            yaml_data = {
                "qemu": {
                    "platform": platform,
                    "image": f"{image_path}/{image_name}.raw" if image_path else None,
                    "ip": "127.0.0.1",
                    "port": 2223,
                    "keep_running": True,
                    "arch": config_data["arch"],
                    "ssh": {
                        "ssh_key_generated": True,
                        "ssh_key_filepath": config_data["ssh_key_filepath"],
                        "user": config_data["ssh_user"],
                    },
                    "features": self.flavors.feature_list
                }
            }
        elif provisioner == "tofu":
            config_file = self.paths.config_dir / f"pytest.{provisioner_pytest}.{flavor}.yaml"
            yaml_data = {
                "manual": {
                    "platform": platform,
                    "host": config_data["host"],
                    "ssh": {
                        "ssh_key_filepath": config_data["ssh_key_filepath"],
                        "user": config_data["ssh_user"]
                    },
                    "features": self.flavors.feature_list
                }
            }

        with config_file.open("w") as yaml_file:
            yaml.dump(yaml_data, yaml_file, default_flow_style=False)

        logger.info(f"Pytest configfile '{config_file.relative_to(self.paths.git_root)}' created.")

class Scripts:
    """Generates configuration files and scripts."""
    def __init__(self, args, paths, flavors):
        self.args = args
        self.paths = paths
        self.flavors = flavors
        self.version = Version(self.paths.git_root)

    def get_image_name(self):
        """Get image_name if not provided."""
        if self.args.image_name:
            return self.args.image_name

        platform = self.flavors.platform
        features = self.flavors.image_features
        arch = self.flavors.arch

        return self.version.get_cname(platform, features, arch)

    def generate_config_data(self, tofu_out=None):
        """Generate config data for pytest and login script."""
        flavor = self.flavors.flavor
        platform = self.flavors.platform
        provisioner = self.args.provisioner

        if provisioner == "qemu":
            ssh_config = {
                "ssh_user": "root",
                "public_ip": "localhost",
                "ssh_private_key": "/root/.ssh/id_ed25519_gardenlinux",
                "ssh_port": 2223
            }
        elif provisioner == "tofu" and tofu_out:
            # Extract values from tofu output
            ssh_config = {
                "ssh_user": tofu_out.get('ssh_users', {}).get('value', {}).get(flavor),
                "public_ip": tofu_out.get('public_ips', {}).get('value', {}).get(flavor),
                "ssh_private_key": tofu_out.get('ssh_private_key', {}).get('value'),
                "ssh_port": 22
            }
            logger.debug(f"Extracted SSH config from tofu output: {ssh_config}")
        else:
            logger.error(f"Unsupported platform {platform} for {flavor}.")
            sys.exit(1)

        logger.info(f"ssh_config: {ssh_config}")
        if not all(ssh_config.values()):
            logger.error(f"Missing required SSH details for {flavor}.")
            sys.exit(1)

        return {
            "provisioner": provisioner,
            "platform": platform,
            "arch": self.flavors.arch,
            "host": ssh_config["public_ip"],
            "ssh_user": ssh_config["ssh_user"],
            "ssh_port": ssh_config["ssh_port"],
            "ssh_key_filepath": ssh_config["ssh_private_key"]
        }

    def generate_login_script(self, config_data):
        """Generate an SSH login script."""
        flavor = self.flavors.flavor
        provisioner = self.args.provisioner

        login_script_file = self.paths.tests_dir / f"login.{provisioner}.{flavor}.sh"
        with login_script_file.open("w") as login_script:
            login_script.write("#!/usr/bin/env bash\n")
            login_script.write(
                f"CMD=\"${{1}}\"\n"
                f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
                f"-l {config_data['ssh_user']} -i {config_data['ssh_key_filepath']} "
                f"-p {config_data['ssh_port']} {config_data['host']} "
                f"\"${{CMD}}\"\n"
            )

        login_script_file.chmod(0o755)
        logger.info(f"Login script '{login_script_file.relative_to(self.paths.git_root)}' created.")

        return config_data

    def generate_scp_local_remote_script(self, config_data):
        """Generate an scp local to remote script."""
        flavor = self.flavors.flavor
        provisioner = self.args.provisioner

        scp_script_file = self.paths.tests_dir / f"scp-local-remote.{provisioner}.{flavor}.sh"
        with scp_script_file.open("w") as scp_script:
            scp_script.write("#!/usr/bin/env bash\n")
            scp_script.write("PATH_LOCAL=${1}\n")
            scp_script.write("PATH_REMOTE=${2:-/var/tmp/gardenlinux}\n")
            scp_script.write(
                f"scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r -P {config_data['ssh_port']} -i {config_data['ssh_key_filepath']} \"${{PATH_LOCAL}}\" \"{config_data['ssh_user']}@{config_data['host']}:${{PATH_REMOTE}}\"\n"
            )

        scp_script_file.chmod(0o755)
        logger.info(f"scp script '{scp_script_file.relative_to(self.paths.git_root)}' created.")

        return config_data

    def generate_scp_remote_local_script(self, config_data):
        """Generate an scp remote to local script."""
        flavor = self.flavors.flavor
        provisioner = self.args.provisioner

        scp_script_file = self.paths.tests_dir / f"scp-remote-local.{provisioner}.{flavor}.sh"
        with scp_script_file.open("w") as scp_script:
            scp_script.write("#!/usr/bin/env bash\n")
            scp_script.write("PATH_LOCAL=${1}\n")
            scp_script.write("PATH_REMOTE=${2:-/var/tmp/gardenlinux}\n")
            scp_script.write(
                f"scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r -P {config_data['ssh_port']} -i {config_data['ssh_key_filepath']} \"{config_data['ssh_user']}@{config_data['host']}:${{PATH_REMOTE}}\" \"${{PATH_LOCAL}}\"\n"
            )

        scp_script_file.chmod(0o755)
        logger.info(f"scp script '{scp_script_file.relative_to(self.paths.git_root)}' created.")

        return config_data

    def generate_pytest_scripts(self):
        """Generate pytest apply and test scripts."""
        flavor = self.flavors.flavor
        provisioner = self.args.provisioner
        provisioner_pytest = PROVISIONER_PYTEST_MAP[provisioner]

        apply_script = self.paths.tests_dir / f"pytest.{provisioner}.{flavor}.apply.sh"
        with apply_script.open("w") as f:
            f.write("#!/usr/bin/env bash\n")
            f.write(
                f"cd {self.paths.tests_dir} && "
                f"pytest -v --provisioner={provisioner_pytest} --configfile config/pytest.{provisioner_pytest}.{flavor}.yaml --create-only\n"
            )
        apply_script.chmod(0o755)

        test_script = self.paths.tests_dir / f"pytest.{provisioner}.{flavor}.test.sh"
        with test_script.open("w") as f:
            f.write("#!/usr/bin/env bash\n")
            f.write(
                f"cd {self.paths.tests_dir} && "
                f"pytest -v --provisioner={provisioner_pytest} --configfile config/pytest.{provisioner_pytest}.{flavor}.yaml\n"
            )
        test_script.chmod(0o755)

        logger.info(f"Pytest script '{apply_script.relative_to(self.paths.git_root)}' created.")
        logger.info(f"Pytest script '{test_script.relative_to(self.paths.git_root)}' created.")

class Tofu:
    """Generates configuration files and scripts."""
    def __init__(self, args, paths, flavor_parser):
        self.paths = paths
        self.flavor_parser = flavor_parser
        self.tofu_dir = self.paths.tofu_dir
        self.scripts = Scripts(args, paths, flavor_parser)

    def get_tofu_output(self, flavor):
        """Get OpenTofu output after ensuring correct workspace and directory."""
        try:
            # Ensure we're in the correct directory
            original_dir = Path.cwd()
            os.chdir(self.tofu_dir)

            # Select the correct workspace
            workspace = f"{flavor}-{self.paths.seed}"
            logger.info(f"Workspace: {workspace}")
            workspace_cmd = ["tofu", "workspace", "select", workspace]
            subprocess.run(workspace_cmd, check=True, capture_output=True, text=True)

            # Get the output
            tofu_output = subprocess.check_output(["tofu", "output", "-json"], text=True)
            tofu_data = json.loads(tofu_output)
            logger.debug(f"tofu_data: {tofu_data}")

            if not tofu_data:
                raise ValueError("No OpenTofu output variables found")

            return tofu_data

        except subprocess.CalledProcessError as e:
            logger.error(f"OpenTofu command failed: {e.stderr}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenTofu output: {e}")
            raise
        finally:
            # Always return to original directory
            os.chdir(original_dir)

    def create_tfvars_file(self, test_prefix, image_path=None, image_name=None):
        """Create .tfvars files for OpenTofu configuration."""
        flavor = self.flavor_parser.flavor
        platform = self.flavor_parser.platform
        arch = self.flavor_parser.arch

        var_file = self.tofu_dir / f"variables.{flavor}.tfvars"
        var_file.parent.mkdir(exist_ok=True)

        # Define instance types for different platforms and architectures
        instance_types = {
            "ali": {"amd64": "ecs.t6-c1m2.large", "arm64": "ecs.g8y.small"},
            "aws": {"amd64": "m5.large", "arm64": "m6g.medium"},
            "azure": {"amd64": "Standard_D4_v4", "arm64": "Standard_D4ps_v5"},
            "gcp": {"amd64": "n1-standard-2", "arm64": "t2a-standard-2"},
            "openstack": {"amd64": "SCS-2V-4-20s", "arm64": "SCS-2V-4-20s"},
        }

        # Define image file extensions for different platforms
        image_files = {
            "ali": "qcow2",
            "aws": "raw",
            "azure": "vhd",
            "gcp": "gcpimage.tar.gz",
            "openstack": "raw",
        }

        # Generate image_name if not provided
        if not image_name:
            image_name = self.scripts.get_image_name()

        # Determine if we should add extension based on image_path
        image_source_type = urlparse(image_path).scheme if image_path else "file"
        image_file = (
            image_name if image_source_type == "cloud"
            else f"{image_name}.{image_files.get(platform, 'raw')}"
        )

        # Determine if we should add extension based on image_path
        image_source_type = image_path.split("://")[0] if image_path else "file"
        image_file = (
            image_name if image_source_type == "cloud"
            else f"{image_name}.{image_files.get(platform, 'raw')}"
        )

        # Create flavor configuration
        flavor_item = {
            "name": flavor,
            "platform": platform,
            "features": self.flavor_parser.feature_list,
            "arch": arch,
            "instance_type": instance_types.get(platform, {}).get(arch),
            "image_file": image_file
        }

        # Write the tfvars file
        with var_file.open('w') as f:
            f.write(f'test_prefix = "{test_prefix}"\n')

            if image_path:
                f.write(f'image_path = "{image_path}"\n')

            flavors_list = [flavor_item]
            formatted_flavors = json.dumps(flavors_list, indent=2)
            f.write(f'flavors = {formatted_flavors}\n')

        logger.info(f"Created OpenTofu variables file: {var_file.relative_to(self.paths.git_root)}")

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate pytest config files and SSH login scripts for platform tests."
    )
    parser.add_argument(
        '--flavor',
        type=str,
        required=True,
        help="The flavor to be tested (e.g., 'kvm-gardener_prod-amd64')."
    )
    parser.add_argument(
        '--provisioner',
        choices=['qemu', 'tofu'],
        required=True,
        help="Provisioner to use: 'qemu' for local testing or 'tofu' for Cloud Provider testing."
    )
    parser.add_argument(
        '--image-path',
        type=str,
        help="Uri and base path for image files (e.g., 'file:///gardenlinux/.build' or 'cloud://').",
        default='file:///gardenlinux/.build'
    )
    parser.add_argument(
        '--image-name',
        type=str,
        help="""
                Image name or image_name style image reference:
                (e.g., image_name: 'kvm-gardener_prod-amd64-1312.0-80ffcc87',
                ali image: 'm-01234567890123456',
                aws ami: 'ami-01234567890123456',
                azure community gallery version: '/communityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/images/gardenlinux-gen2/versions/1443.18.0',
                gcp image: 'projects/sap-se-gcp-gardenlinux/global/images/gardenlinux-gcp-gardener-prod-arm64-1443-18-97fd20ac'.
            """
    )
    parser.add_argument(
        '--cname',
        type=str,
        help="Basename of image file (e.g., 'kvm-gardener_prod-amd64-1312.0-80ffcc87')."
    )
    parser.add_argument(
        '--image-name',
        type=str,
        help="""
                Image name or image_name style image reference:
                (e.g., image_name: 'kvm-gardener_prod-amd64-1312.0-80ffcc87',
                ali image: 'm-01234567890123456',
                aws ami: 'ami-01234567890123456',
                azure community gallery version: '/communityGalleries/gardenlinux-13e998fe-534d-4b0a-8a27-f16a73aef620/images/gardenlinux-gen2/versions/1443.18.0',
                gcp image: 'projects/sap-se-gcp-gardenlinux/global/images/gardenlinux-gcp-gardener-prod-arm64-1443-18-97fd20ac'.
            """
    )
    parser.add_argument(
        '--test-prefix',
        type=str,
        help="Test prefix for OpenTofu variable files."
    )
    parser.add_argument(
        '--create-tfvars',
        action='store_true',
        help="Create OpenTofu variables file."
    )

    return parser.parse_args()

def main():
    args = parse_arguments()

    # Initialize core components
    path = PathManager()
    flavor = Flavors(args, path)
    scripts = Scripts(args, path, flavor)
    pytest = PytestConfig(args, path, flavor, scripts)
    tofu = Tofu(args, path, flavor)

    if args.provisioner == 'qemu':
        config_data = scripts.generate_config_data()
        scripts.generate_login_script(config_data)
        scripts.generate_scp_local_remote_script(config_data)
        pytest.generate_pytest_configfile(
            config_data,
            image_path=args.image_path,
            image_name=args.image_name,
        )
        scripts.generate_pytest_scripts()

    elif args.provisioner == 'tofu':
        try:
            if args.create_tfvars:
                if not args.test_prefix:
                    logger.error("test_prefix is required when creating tfvars file")
                    sys.exit(1)
                tofu.create_tfvars_file(
                    args.test_prefix,
                    image_path=args.image_path,
                    image_name=args.image_name,
                )
            else:
                tofu_data = tofu.get_tofu_output(args.flavor)
                config_data = scripts.generate_config_data(tofu_data)
                scripts.generate_login_script(config_data)
                scripts.generate_scp_local_remote_script(config_data)
                pytest.generate_pytest_configfile(config_data)

        except Exception as e:
            logger.error(f"OpenTofu error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
