#!/usr/bin/env python3

from botocore import UNSIGNED
from botocore.client import Config
from gardenlinux.apt import DebsrcFile
from gardenlinux.features import CName
from gardenlinux.flavors import Parser as FlavorsParser
from gardenlinux.s3 import S3Artifacts
from pathlib import Path
from yaml.loader import SafeLoader
import argparse
import boto3
import gzip
import json
import os
import re
import requests
import shutil
import subprocess
import sys
from git import Repo
import textwrap
import yaml
import urllib.request

from get_kernelurls import get_kernel_urls


GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME="gardenlinux-github-releases"


cloud_fullname_dict = {
    'ali': 'Alibaba Cloud',
    'aws': 'Amazon Web Services',
    'gcp': 'Google Cloud Platform',
    'azure': 'Microsoft Azure',
    'openstack': 'OpenStack',
    'openstackbaremetal': 'OpenStack Baremetal'
}

# https://github.com/gardenlinux/gardenlinux/issues/3044
# Empty string is the 'legacy' variant with traditional root fs and still needed/supported
IMAGE_VARIANTS = ['', '_usi', '_tpm2_trustedboot']

# Variant display names and order for consistent use across functions
VARIANT_ORDER = ['legacy', 'usi', 'tpm2_trustedboot']
VARIANT_NAMES = {
    'legacy': 'Default',
    'usi': 'USI (Unified System Image)',
    'tpm2_trustedboot': 'TPM2 Trusted Boot'
}

# Mapping from image variant suffixes to variant keys
VARIANT_SUFFIX_MAP = {
    '': 'legacy',
    '_usi': 'usi',
    '_tpm2_trustedboot': 'tpm2_trustedboot'
}

# Short display names for table view
VARIANT_TABLE_NAMES = {
    'legacy': 'Default',
    'usi': 'USI',
    'tpm2_trustedboot': 'TPM2'
}

def get_variant_from_flavor(flavor_name):
    """
    Determine the variant from a flavor name by checking for variant suffixes.
    Returns the variant key (e.g., 'legacy', 'usi', 'tpm2_trustedboot').
    """
    match flavor_name:
        case name if '_usi' in name:
            return 'usi'
        case name if '_tpm2_trustedboot' in name:
            return 'tpm2_trustedboot'
        case _:
            return 'legacy'

def get_platform_release_note_data(metadata, platform):
    """
    Get the appropriate cloud release note data based on platform.
    Returns the structured data dictionary.
    """
    match platform:
        case 'ali':
            return _ali_release_note(metadata)
        case 'aws':
            return _aws_release_note(metadata)
        case 'gcp':
            return _gcp_release_note(metadata)
        case 'azure':
            return _azure_release_note(metadata)
        case 'openstack':
            return _openstack_release_note(metadata)
        case 'openstackbaremetal':
            return _openstackbaremetal_release_note(metadata)
        case _:
            print(f"unknown platform {platform}")
            return None

def get_file_extension_for_platform(platform):
    """
    Get the correct file extension for a given platform.
    """
    match platform:
        case 'ali':
            return '.qcow2'
        case 'gcp':
            return '.gcpimage.tar.gz'
        case 'azure':
            return '.vhd'
        case 'aws' | 'openstack' | 'openstackbaremetal':
            return '.raw'
        case _:
            return '.raw'  # Default fallback

def get_platform_display_name(platform):
    """
    Get the display name for a platform.
    """
    match platform:
        case 'ali' | 'openstackbaremetal' | 'openstack' | 'azure' | 'gcp' | 'aws':
            return cloud_fullname_dict[platform]
        case _:
            return platform.upper()

def _ali_release_note(metadata):
    published_image_metadata = metadata['published_image_metadata']
    flavor_name = metadata['s3_key'].split('/')[-1]  # Extract flavor from s3_key

    regions = []
    for pset in published_image_metadata:
        for p in published_image_metadata[pset]:
            regions.append({
                'region': p['region_id'],
                'image_id': p['image_id']
            })

    return {
        'flavor': flavor_name,
        'regions': regions
    }


def _aws_release_note(metadata):
    published_image_metadata = metadata['published_image_metadata']
    flavor_name = metadata['s3_key'].split('/')[-1]  # Extract flavor from s3_key

    regions = []
    for pset in published_image_metadata:
        for p in published_image_metadata[pset]:
            regions.append({
                'region': p['aws_region_id'],
                'image_id': p['ami_id']
            })

    return {
        'flavor': flavor_name,
        'regions': regions
    }


def _gcp_release_note(metadata):
    published_image_metadata = metadata['published_image_metadata']
    flavor_name = metadata['s3_key'].split('/')[-1]  # Extract flavor from s3_key

    details = {}
    if 'gcp_image_name' in published_image_metadata:
        details['image_name'] = published_image_metadata['gcp_image_name']
    if 'gcp_project_name' in published_image_metadata:
        details['project'] = published_image_metadata['gcp_project_name']
    details['availability'] = "Global (all regions)"

    return {
        'flavor': flavor_name,
        'details': details
    }


def _openstack_release_note(metadata):
    published_image_metadata = metadata['published_image_metadata']
    flavor_name = metadata['s3_key'].split('/')[-1]  # Extract flavor from s3_key

    regions = []
    if 'published_openstack_images' in published_image_metadata:
        for image in published_image_metadata['published_openstack_images']:
            regions.append({
                'region': image['region_name'],
                'image_id': image['image_id'],
                'image_name': image['image_name']
            })

    return {
        'flavor': flavor_name,
        'regions': regions
    }


def _openstackbaremetal_release_note(metadata):
    published_image_metadata = metadata['published_image_metadata']
    flavor_name = metadata['s3_key'].split('/')[-1]  # Extract flavor from s3_key

    regions = []
    if 'published_openstack_images' in published_image_metadata:
        for image in published_image_metadata['published_openstack_images']:
            regions.append({
                'region': image['region_name'],
                'image_id': image['image_id'],
                'image_name': image['image_name']
            })

    return {
        'flavor': flavor_name,
        'regions': regions
    }


def _azure_release_note(metadata):
    published_image_metadata = metadata['published_image_metadata']
    flavor_name = metadata['s3_key'].split('/')[-1]  # Extract flavor from s3_key

    gallery_images = []
    marketplace_images = []

    for pset in published_image_metadata:
        if pset == 'published_gallery_images':
            for gallery_image in published_image_metadata[pset]:
                gallery_images.append({
                    'hyper_v_generation': gallery_image['hyper_v_generation'],
                    'azure_cloud': gallery_image['azure_cloud'],
                    'image_id': gallery_image['community_gallery_image_id']
                })

        if pset == 'published_marketplace_images':
            for market_image in published_image_metadata[pset]:
                marketplace_images.append({
                    'hyper_v_generation': market_image['hyper_v_generation'],
                    'urn': market_image['urn']
                })

    return {
        'flavor': flavor_name,
        'gallery_images': gallery_images,
        'marketplace_images': marketplace_images
    }

def generate_release_note_image_ids(metadata_files):
    """
    Groups metadata files by image variant, then platform, then architecture
    """
    # Group metadata by variant, platform, and architecture
    grouped_data = {}

    for metadata_file_path in metadata_files:
        with open(metadata_file_path) as f:
            metadata = yaml.load(f, Loader=SafeLoader)

        published_image_metadata = metadata['published_image_metadata']
        # Skip if no publishing metadata found
        if published_image_metadata is None:
            continue

        platform = metadata['platform']
        arch = metadata['architecture']

        # Determine variant from flavor name
        flavor_name = metadata['s3_key'].split('/')[-1]
        variant = get_variant_from_flavor(flavor_name)

        if variant not in grouped_data:
            grouped_data[variant] = {}
        if platform not in grouped_data[variant]:
            grouped_data[variant][platform] = {}
        if arch not in grouped_data[variant][platform]:
            grouped_data[variant][platform][arch] = []

        grouped_data[variant][platform][arch].append(metadata)

    # Generate both table and old format
    output = "## Published Images\n\n"

    # Add table format (collapsed by default)
    output += "<details>\n<summary>📊 Table View</summary>\n\n"
    output += generate_table_format(grouped_data)
    output += "\n</details>\n\n"

    # Add old format (collapsed by default)
    output += "<details>\n<summary>📝 Detailed View</summary>\n\n"
    output += generate_detailed_format(grouped_data)
    output += "\n</details>\n\n"

    return output

def generate_table_format(grouped_data):
    """
    Generate the table format with collapsible region details
    """
    output = "| Variant | Platform | Architecture | Flavor | Regions & Image IDs | Download Links |\n"
    output += "|---------|----------|--------------|--------|---------------------|----------------|\n"

    for variant in VARIANT_ORDER:
        if variant not in grouped_data:
            continue

        for platform in sorted(grouped_data[variant].keys()):
            platform_display = get_platform_display_name(platform)

            for arch in sorted(grouped_data[variant][platform].keys()):
                # Process all metadata for this variant/platform/architecture
                for metadata in grouped_data[variant][platform][arch]:
                    data = get_platform_release_note_data(metadata, platform)
                    if data is None:
                        continue

                    # Generate collapsible details for regions
                    details_content = generate_region_details(data, platform)
                    summary_text = generate_summary_text(data, platform)

                    # Generate download links
                    download_links = generate_download_links(data['flavor'], platform)

                    # Use shorter names for table display
                    variant_display = VARIANT_TABLE_NAMES[variant]
                    output += f"| {variant_display} | {platform_display} | {arch} | `{data['flavor']}` | <details><summary>{summary_text}</summary><br>{details_content}</details> | <details><summary>Download</summary><br>{download_links}</details> |\n"

    return output

def generate_region_details(data, platform):
    """
    Generate the detailed region information for the collapsible section
    """
    details = ""

    match data:
        case {'regions': regions}:
            for region in regions:
                match region:
                    case {'region': region_name, 'image_id': image_id, 'image_name': image_name}:
                        details += f"**{region_name}:** {image_id} ({image_name})<br>"
                    case {'region': region_name, 'image_id': image_id}:
                        details += f"**{region_name}:** {image_id}<br>"
        case {'details': details_dict}:
            for key, value in details_dict.items():
                details += f"**{key.replace('_', ' ').title()}:** {value}<br>"
        case {'gallery_images': gallery_images, 'marketplace_images': marketplace_images}:
            if gallery_images:
                details += "**Gallery Images:**<br>"
                for img in gallery_images:
                    details += f"• {img['hyper_v_generation']} ({img['azure_cloud']}): {img['image_id']}<br>"
            if marketplace_images:
                details += "**Marketplace Images:**<br>"
                for img in marketplace_images:
                    details += f"• {img['hyper_v_generation']}: {img['urn']}<br>"
        case {'gallery_images': gallery_images}:
            details += "**Gallery Images:**<br>"
            for img in gallery_images:
                details += f"• {img['hyper_v_generation']} ({img['azure_cloud']}): {img['image_id']}<br>"
        case {'marketplace_images': marketplace_images}:
            details += "**Marketplace Images:**<br>"
            for img in marketplace_images:
                details += f"• {img['hyper_v_generation']}: {img['urn']}<br>"

    return details

def generate_summary_text(data, platform):
    """
    Generate the summary text for the collapsible section
    """
    match data:
        case {'regions': regions}:
            count = len(regions)
            return f"{count} regions"
        case {'details': _}:
            return "Global availability"
        case {'gallery_images': gallery_images, 'marketplace_images': marketplace_images}:
            gallery_count = len(gallery_images)
            marketplace_count = len(marketplace_images)
            return f"{gallery_count} gallery + {marketplace_count} marketplace images"
        case {'gallery_images': gallery_images}:
            gallery_count = len(gallery_images)
            return f"{gallery_count} gallery images"
        case {'marketplace_images': marketplace_images}:
            marketplace_count = len(marketplace_images)
            return f"{marketplace_count} marketplace images"
        case _:
            return "Details available"

def generate_download_links(flavor, platform):
    """
    Generate download links for the flavor with correct file extension based on platform
    """
    base_url = "https://gardenlinux-github-releases.s3.amazonaws.com/objects"
    file_ext = get_file_extension_for_platform(platform)
    filename = f"{flavor}{file_ext}"
    download_url = f"{base_url}/{flavor}/{filename}"
    return f"[{filename}]({download_url})"

def generate_detailed_format(grouped_data):
    """
    Generate the old detailed format with YAML
    """
    output = ""

    for variant in VARIANT_ORDER:
        if variant not in grouped_data:
            continue

        output += f"<details>\n<summary>Variant - {VARIANT_NAMES[variant]}</summary>\n\n"
        output += f"### Variant - {VARIANT_NAMES[variant]}\n\n"

        for platform in sorted(grouped_data[variant].keys()):
            platform_long_name = cloud_fullname_dict.get(platform, platform)
            output += f"<details>\n<summary>{platform.upper()} - {platform_long_name}</summary>\n\n"
            output += f"#### {platform.upper()} - {platform_long_name}\n\n"

            for arch in sorted(grouped_data[variant][platform].keys()):
                output += f"<details>\n<summary>{arch}</summary>\n\n"
                output += f"##### {arch}\n\n"
                output += "```\n"

                # Process all metadata for this variant/platform/architecture
                for metadata in grouped_data[variant][platform][arch]:
                    data = get_platform_release_note_data(metadata, platform)
                    if data is None:
                        continue

                    # Format the data according to the new structure as YAML
                    output += f"- flavor: {data['flavor']}\n"

                    # Add download link with correct file extension
                    file_ext = get_file_extension_for_platform(platform)

                    filename = f"{data['flavor']}{file_ext}"
                    download_url = f"https://gardenlinux-github-releases.s3.amazonaws.com/objects/{data['flavor']}/{filename}"
                    output += f"  download_url: {download_url}\n"

                    if 'regions' in data:
                        output += "  regions:\n"
                        for region in data['regions']:
                            if 'image_name' in region:
                                output += f"    - region: {region['region']}\n"
                                output += f"      image_id: {region['image_id']}\n"
                                output += f"      image_name: {region['image_name']}\n"
                            else:
                                output += f"    - region: {region['region']}\n"
                                output += f"      image_id: {region['image_id']}\n"
                    elif 'details' in data and platform != 'gcp':
                        output += "  details:\n"
                        for key, value in data['details'].items():
                            output += f"    {key}: {value}\n"
                    elif platform == 'gcp' and 'details' in data:
                        # For GCP, move details up to same level as flavor
                        for key, value in data['details'].items():
                            output += f"  {key}: {value}\n"
                    elif 'gallery_images' in data or 'marketplace_images' in data:
                        if data.get('gallery_images'):
                            output += "  gallery_images:\n"
                            for img in data['gallery_images']:
                                output += f"    - hyper_v_generation: {img['hyper_v_generation']}\n"
                                output += f"      azure_cloud: {img['azure_cloud']}\n"
                                output += f"      image_id: {img['image_id']}\n"
                        if data.get('marketplace_images'):
                            output += "  marketplace_images:\n"
                            for img in data['marketplace_images']:
                                output += f"    - hyper_v_generation: {img['hyper_v_generation']}\n"
                                output += f"      urn: {img['urn']}\n"

                output += "```\n\n"
                output += "</details>\n\n"

            output += "</details>\n\n"

        output += "</details>\n\n"

    return output

def download_metadata_file(s3_artifacts, cname, artifacts_dir):
    """
    Download metadata file (s3_metadata.yaml)
    """
    release_object = list(
        s3_artifacts._bucket.objects.filter(Prefix=f"meta/singles/{cname}")
    )[0]
    s3_artifacts._bucket.download_file(
        release_object.key, artifacts_dir.joinpath(f"{cname}.s3_metadata.yaml")
    )


def download_all_metadata_files(version, commitish):
    repo = Repo(".")
    commit = repo.commit(commitish)
    flavors_data = commit.tree["flavors.yaml"].data_stream.read().decode('utf-8')
    flavors = FlavorsParser(flavors_data).filter(only_publish=True)

    local_dest_path = Path("s3_downloads")
    if local_dest_path.exists():
        shutil.rmtree(local_dest_path)
    local_dest_path.mkdir(mode=0o755, exist_ok=False)

    s3_artifacts = S3Artifacts(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME)

    for flavor in flavors:
        cname = CName(flavor[1], flavor[0], "{0}-{1}".format(version, commitish))
        # Filter by image variants - only download if the flavor matches one of the variants
        flavor_matches_variant = False
        for variant_suffix in IMAGE_VARIANTS:
            if variant_suffix == '':
                last_part = cname.cname.split("-")[-1]
                if "_" not in last_part:
                    flavor_matches_variant = True
                    break
            elif variant_suffix in cname.cname:
                # Specific variant (any non-empty string in IMAGE_VARIANTS)
                flavor_matches_variant = True
                break

        if not flavor_matches_variant:
            print(f"INFO: Skipping flavor {cname.cname} - not matching image variants filter")
            continue

        try:
            download_metadata_file(s3_artifacts, cname.cname, local_dest_path)
        except IndexError:
            print(f"WARNING: No artifacts found for flavor {cname.cname}, skipping...")
            continue

    return [ str(artifact) for artifact in local_dest_path.iterdir() ]





def _parse_match_section(pkg_list: list):
    output = ""
    for pkg in pkg_list:
        # If is dict, the package has additional information relevant for release notes
        if isinstance(pkg, dict):
            pkg_string = next(iter(pkg))
            output += f"\n{pkg_string}:\n"
            for item in pkg[pkg_string]:
                for k,v in item.items():
                    output += f"  * {k}: {v}\n"
    return output

def release_notes_changes_section(gardenlinux_version):
    """
        Get list of fixed CVEs, grouped by upgraded package.
        Note: This result is not perfect, feel free to edit the generated release notes and
        file issues in glvd for improvement suggestions https://github.com/gardenlinux/glvd/issues
    """
    try:
        url = f"https://glvd.ingress.glvd.gardnlinux.shoot.canary.k8s-hana.ondemand.com/v1/patchReleaseNotes/{gardenlinux_version}"
        response = requests.get(url)
        response.raise_for_status()  # Will raise an error for bad responses
        data = response.json()

        if len(data["packageList"]) == 0:
            return ""

        output = [
            "## Changes",
            "The following packages have been upgraded, to address the mentioned CVEs:"
        ]
        for package in data["packageList"]:
            upgrade_line = (
                f"- upgrade '{package['sourcePackageName']}' from `{package['oldVersion']}` "
                f"to `{package['newVersion']}`"
            )
            output.append(upgrade_line)

            if package["fixedCves"]:
                for fixedCve in package["fixedCves"]:
                    output.append(f'  - {fixedCve}')

        return "\n".join(output) + "\n\n"
    except:
        # There are expected error cases, for example with versions not supported by glvd (1443.x) or when the api is not available
        # Fail gracefully by adding the placeholder we previously used, so that the release note generation does not fail.
        return textwrap.dedent("""
        ## Changes
        The following packages have been upgraded, to address the mentioned CVEs:
        **todo release facilitator: fill this in**
        """)

def release_notes_software_components_section(package_list):
    output = "## Software Component Versions\n"
    output += "```"
    output += "\n"
    packages_regex = re.compile(r'^linux-image-amd64$|^systemd$|^containerd$|^runc$|^curl$|^openssl$|^openssh-server$|^libc-bin$')
    for entry in package_list.values():
        if packages_regex.match(entry.deb_source):
            output += f'{entry!r}\n'
    output += "```"
    output += "\n\n"
    return output

def release_notes_compare_package_versions_section(gardenlinux_version, package_list):
    output = ""
    version_components = gardenlinux_version.split('.')
    # Assumes we always have version numbers like 1443.2
    if (len(version_components) == 2):
        try:
            major = int(version_components[0])
            patch = int(version_components[1])

            if patch > 0:
                previous_version = f"{major}.{patch - 1}"

                output += f"## Changes in Package Versions Compared to {previous_version}\n"
                output += "```diff\n"
                output += subprocess.check_output(['/usr/bin/env', 'bash','./hack/compare-apt-repo-versions.sh', previous_version, gardenlinux_version]).decode("utf-8")
                output += "```\n\n"
            elif patch == 0:
                output += f"## Full List of Packages in Garden Linux version {major}\n"
                output += "<details><summary>Expand to see full list</summary>\n"
                output += "<pre>"
                output += "\n"
                for entry in package_list.values():
                    output += f'{entry!r}\n'
                output += "</pre>"
                output += "\n</details>\n\n"

        except ValueError:
            print(f"Could not parse {gardenlinux_version} as the Garden Linux version, skipping version compare section")
    else:
        print(f"Unexpected version number format {gardenlinux_version}, expected format (major is int).(patch is int)")
    return output


def _get_package_list(gardenlinux_version):
    (path, headers) = urllib.request.urlretrieve(f'https://packages.gardenlinux.io/gardenlinux/dists/{gardenlinux_version}/main/binary-amd64/Packages.gz')
    with gzip.open(path, 'rt') as f:
        d = DebsrcFile()
        d.read(f)
        return d

def create_github_release_notes(gardenlinux_version, commitish):
    commitish_short=commitish[:8]

    package_list = _get_package_list(gardenlinux_version)

    output = ""

    output += release_notes_changes_section(gardenlinux_version)

    output += release_notes_software_components_section(package_list)

    output += release_notes_compare_package_versions_section(gardenlinux_version, package_list)

    metadata_files = download_all_metadata_files(gardenlinux_version, commitish_short)

    output += generate_release_note_image_ids(metadata_files)

    output += "\n"
    output += "## Kernel Package direct download links\n"
    output += get_kernel_urls(gardenlinux_version)
    output += "\n"
    output += "## Kernel Module Build Container (kmodbuild) "
    output += "\n"
    output += "```"
    output += "\n"
    output += f"ghcr.io/gardenlinux/gardenlinux/kmodbuild:{gardenlinux_version}"
    output += "\n"
    output += "```"
    output += "\n"
    return output

def write_to_release_id_file(release_id):
    try:
        with open('.github_release_id', 'w') as file:
            file.write(release_id)
        print(f"Created .github_release_id successfully.")
    except IOError as e:
        print(f"Could not create .github_release_id file: {e}")
        sys.exit(1)

def create_github_release(owner, repo, tag, commitish, body):

    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        raise ValueError("GITHUB_TOKEN environment variable not set")

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    data = {
        'tag_name': tag,
        'target_commitish': commitish,
        'name': tag,
        'body': body,
        'draft': False,
        'prerelease': False
    }

    response = requests.post(f'https://api.github.com/repos/{owner}/{repo}/releases', headers=headers, data=json.dumps(data))

    if response.status_code == 201:
        print("Release created successfully")
        response_json = response.json()
        return response_json.get('id')
    else:
        print("Failed to create release")
        print(response.json())
        response.raise_for_status()

def main():
    parser = argparse.ArgumentParser(description="GitHub Release Script")
    subparsers = parser.add_subparsers(dest='command')

    create_parser = subparsers.add_parser('create')
    create_parser.add_argument('--owner', default="gardenlinux")
    create_parser.add_argument('--repo', default="gardenlinux")
    create_parser.add_argument('--tag', required=True)
    create_parser.add_argument('--commit', required=True)
    create_parser.add_argument('--dry-run', action='store_true', default=False)

    upload_parser = subparsers.add_parser('upload')
    upload_parser.add_argument('--release_id', required=True)
    upload_parser.add_argument('--file_path', required=True)

    kernelurl_parser = subparsers.add_parser('kernelurls')
    kernelurl_parser.add_argument('--version', required=True)
    args = parser.parse_args()

    if args.command == 'create':
        body = create_github_release_notes(args.tag, args.commit)
        if not args.dry_run:
            release_id = create_github_release(args.owner, args.repo, args.tag, args.commit, body)
            write_to_release_id_file(f"{release_id}")
            print(f"Release created with ID: {release_id}")
        else:
            print(body)
    elif args.command == 'upload':
        # Implementation for 'upload' command
        pass
    elif args.command == 'kernelurls':
        # Implementation for 'upload' command
        output =""
        output += "## Kernel Package direct download links\n"
        output += get_kernel_urls(args.version)
        print(output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
