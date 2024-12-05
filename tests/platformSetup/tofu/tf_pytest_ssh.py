#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path
import yaml


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
        description="Generate a pytest configfile and a SSH login script for platform tests built up with OpenTofu."
    )
    parser.add_argument("flavor", nargs="?", help="The flavor name (e.g., 'gcp-gardener_prod-amd64')")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return parser.parse_args()


def parse_features(flavor):
    """Parse features from the flavor name."""
    parts = flavor.split("-")
    
    if len(parts) < 3:
        print("Error: Flavor name must be in the format 'platform-features-arch'")
        sys.exit(1)

    # Extract platform (first part) and architecture (last part)
    platform = parts[0]
    arch = parts[-1]
    
    # All middle parts are features, split them by '_' to expand multi-part features
    raw_features = "-".join(parts[1:-1]).replace("_", "-_")  # Rejoin middle parts to handle mixed cases
    feature_list = [feature for feature in raw_features.split("-")]

    # Always add the base and platform features
    feature_list.append("base")
    feature_list.append(platform)

    # Ensure features are resolved recursively
    feature_list = resolve_features_recursively(feature_list)

    print(f"Flavor: {flavor}")
    print(f"Platform: {platform}")
    print(f"Features: {feature_list}")
    print(f"Architecture: {arch}")

    return platform, feature_list, arch


def get_includes_from_yaml(file_path):
    try:
        with open(file_path, "r") as yaml_file:
            data = yaml.safe_load(yaml_file)
            return data.get("features", {}).get("include", [])
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def resolve_features_recursively(features):
    """Recursively resolve feature includes using info.yaml files."""
    git_root = get_git_root()
    base_directory = git_root / "features"
    features_recursive = set(features)

    for feature in features:
        feature_path = Path(base_directory) / feature
        if feature_path.is_dir():
            info_file_path = feature_path / "info.yaml"
            if info_file_path.is_file():
                includes = get_includes_from_yaml(info_file_path)
                features_recursive.update(includes)
            else:
                print(f"info.yaml not found in {feature_path}")
        else:
            print(f"Feature folder {feature} not found in {base_directory}")

    return list(features_recursive)


def get_tofu_output_variables():
    """Get tofu output variables."""
    try:
        tofu_output = subprocess.check_output(["tofu", "output", "-json"], text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to execute 'tofu output -json': {e}")
        sys.exit(1)

    try:
        data = json.loads(tofu_output)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON output: {e}")
        sys.exit(1)

    # Convert the JSON into a dictionary of variables
    tofu_out = {}
    if len(data.items()) != 0:
        for key, value in data.items():
            if "value" in value:
                tofu_out[key] = value["value"]
    else:
        print(f"Error: No tofu output variables found")
        sys.exit(1)

    return tofu_out


def generate_login_script(flavor, platform, arch, feature_list, tofu_out):
    """Generate an SSH login script using the environment variables."""
    flavor_safe = flavor.replace("-", "_")
    ssh_user = tofu_out.get('ssh_users', {}).get(flavor, None)
    public_ip = tofu_out.get('public_ips', {}).get(flavor, None)
    ssh_private_key = tofu_out.get("ssh_private_key")

    if not ssh_user or not public_ip or not ssh_private_key:
        print(f"Error: Missing required SSH details for {flavor}.")
        sys.exit(1)

    login_script_file = Path.cwd() / f"login.{flavor}.sh"
    with login_script_file.open("w") as login_script:
        login_script.write("#!/usr/bin/env bash\n")
        login_script.write(
            f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
            f"-l {ssh_user} -i {ssh_private_key} {public_ip}\n"
        )

    login_script_file.chmod(0o755)
    print(f"Login script '{login_script_file.resolve()}' created and made executable.")

    return {
        "platform": platform,
        "host": public_ip,
        "ssh_user": ssh_user,
        "ssh_key_filepath": ssh_private_key
    }


def generate_pytest_configfile(flavor, config_data, feature_list):
    """Generate a pytest configfile for the specified flavor."""
    git_root = get_git_root()
    config_dir = git_root / "tests/config"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / f"manual_{flavor}.yaml"
    yaml_data = {
        "manual": {
            "platform": config_data["platform"],
            "host": config_data["host"],
            "ssh": {
                "ssh_key_filepath": config_data["ssh_key_filepath"],
                "user": config_data["ssh_user"]
            },
            "features": feature_list
        }
    }

    with config_file.open("w") as yaml_file:
        yaml.dump(yaml_data, yaml_file, default_flow_style=False)

    print(f"pytest configfile '{config_file.resolve()}' created.")


def main():
    args = parse_arguments()
    platform, feature_list, arch = parse_features(args.flavor)
    tofu_out = get_tofu_output_variables()
    config_data = generate_login_script(args.flavor, platform, arch, feature_list, tofu_out)
    generate_pytest_configfile(args.flavor, config_data, feature_list)


if __name__ == "__main__":
    main()
