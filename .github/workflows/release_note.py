#!/usr/bin/env python3
import os
import requests
import json
import boto3
import botocore
import yaml
from yaml.loader import SafeLoader
import sys
import urllib.request
from botocore import UNSIGNED
from botocore.client import Config
import argparse
import gzip
import re
import subprocess
import textwrap

from get_kernelurls import get_kernel_urls
from parse_aptsource import DebsrcFile

GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME="gardenlinux-github-releases"

arches = [
    'amd64',
    'arm64'
]

cloud_fullname_dict = {
    'ali': 'Alibaba Cloud',
    'aws': 'Amazon Web Services',
    'gcp': 'Google Cloud Platform',
    'azure': 'Microsoft Azure'
}


def _ali_release_note(published_image_metadata):
    output = ""
    for pset in published_image_metadata:
        for p in published_image_metadata[pset]:
            for image in published_image_metadata:
                output += f"- Region: {p['region_id']}, Image-Id: {p['image_id']}\n"
    return output


def _aws_release_note(published_image_metadata):
    output = ""
    for pset in published_image_metadata:
        for p in published_image_metadata[pset]:
            for image in published_image_metadata:
                output += f"- Region: {p['aws_region_id']}, Image-Id: {p['ami_id']}\n"
    return output


def _gcp_release_note(published_image_metadata):
    return f"gcp_image_name: {published_image_metadata['gcp_image_name']}\n"


def _azure_release_note(published_image_metadata):
    output = ""
    for pset in published_image_metadata:
        if pset == 'published_gallery_images':
            if (len(published_image_metadata[pset]) > 0):
                output += "# all regions (community gallery image):\n"
            for gallery_image in published_image_metadata[pset]:
                output += f"Hyper V: {gallery_image['hyper_v_generation']}, "
                # output += f"Azure Cloud: {gallery_image['azure_cloud']}, "
                output += f"Image Id: {gallery_image['community_gallery_image_id']}\n"

        if pset == 'published_marketplace_images':
            if (len(published_image_metadata[pset]) > 0):
                output += "# all regions (marketplace image):\n"
            for market_image in published_image_metadata[pset]:
                output += f"Hyper V: {market_image['hyper_v_generation']}, "
                output += f"urn: {market_image['urn']}\n"
    return output

def generate_release_note_image_ids(manifests):
    out = ""
    for m in manifests:
        out += generate_release_note_image_id_single(m)
    return out

def generate_release_note_image_id_single(manifest_path):
    """
    Outputs a markdown formated string for github release notes,
    containing the image-ids for the respective cloud regions
    """
    output = ""
    with open(manifest_path) as f:
        manifest_data = yaml.load(f, Loader=SafeLoader)
    published_image_metadata = manifest_data['published_image_metadata']

    # No publishing metadata found in manifest, assume it was not published
    if published_image_metadata is None:
        return ""

    platform_short_name = manifest_data['platform']
    arch = manifest_data['architecture']
    if platform_short_name in cloud_fullname_dict:
        platform_long_name = cloud_fullname_dict[platform_short_name]
        output = output + f"### {platform_long_name} ({arch})\n"
    else:
        output = output + f"### {platform_short_name} ({arch})\n"

    output += "```\n"
    if platform_short_name == 'ali':
        output += _ali_release_note(published_image_metadata)
    elif platform_short_name == 'aws':
        output += _aws_release_note(published_image_metadata)
    elif platform_short_name == 'gcp':
        output += _gcp_release_note(published_image_metadata)
    elif platform_short_name == 'azure':
        output += _azure_release_note(published_image_metadata)
    else:
        print(f"unknown platform {platform_short_name}")
    output += "```\n"
    return output


def construct_full_image_name(platform, features, arch, version, commitish):
    return f"{platform}-{features}-{arch}-{version}-{commitish}"


def download_s3_file(bucket, remote_filename, local_filename):
    # Note: No need to sign the request. Features that would require the client to authenticate itself are not used.
    #       Use case here is to simply download public data.
    s3_client = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    s3_client.download_file(bucket, remote_filename, local_filename)


def download_meta_single_manifest(bucket, bucket_path, image_name, dest_path):
    download_s3_file(bucket, f"{bucket_path}/{image_name}", f"{dest_path}/{image_name}")
    return f"{dest_path}/{image_name}"


def download_all_singles(version, commitish):
    if commitish == None:
        raise Exception("Commitish is not set")
    local_dest_path = "s3_downloads"
    os.makedirs(local_dest_path, exist_ok=True)
    manifests = list()
    for a in arches:
        for p in cloud_fullname_dict:
            fname = construct_full_image_name(p, "gardener_prod", a, version, commitish)
            try:
                manifests.append(download_meta_single_manifest(GARDENLINUX_GITHUB_RELEASE_BUCKET_NAME, "meta/singles", fname, "s3_downloads/"))
            except Exception as e:
                print(f"Failed to get manifest. Error: {e}")
                print(f"\tfname: meta/singles/{fname}")
                # Abort generation of Release Notes - Let the CI fail
                sys.exit(1)

    return manifests

def get_image_object_url(bucket, object, expiration=0):
    s3_config = botocore.config.Config(signature_version=botocore.UNSIGNED)
    s3_client = boto3.client('s3', config=s3_config)
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': object}, ExpiresIn = expiration)
    return url


def generate_image_download_section(manifests, version, commitish):
    output = ""
    for manifest_path in manifests:
        with open(manifest_path) as f:
            manifest_data = yaml.load(f, Loader=SafeLoader)
        arch = manifest_data['architecture'].upper()
        platform = manifest_data['platform']
        paths = manifest_data['paths']

        for path in paths:
            if platform == 'ali' and '.qcow2' == path['suffix']:
                output += f"### {cloud_fullname_dict['ali']} ({arch})\n"
                output += f"* [{version}-{commitish}-rootfs.qcow2]({get_image_object_url(path['s3_bucket_name'], path['s3_key'])})\n"
            elif platform == 'aws' and '.raw' == path['suffix']:
                output += f"### {cloud_fullname_dict['aws']} ({arch})\n"
                output += f"* [{version}-{commitish}-rootfs.raw]({get_image_object_url(path['s3_bucket_name'], path['s3_key'])})\n"
            elif platform == 'gcp' and '.tar.gz' == path['suffix']:
                output += f"### {cloud_fullname_dict['gcp']} ({arch})\n"
                output += f"* [{version}-{commitish}-rootfs-gcpimage.tar.gz]({get_image_object_url(path['s3_bucket_name'], path['s3_key'])})\n"
            elif platform == 'azure' and '.vhd' == path['suffix']:
                output += f"### {cloud_fullname_dict['azure']} ({arch})\n"
                output += f"* [{version}-{commitish}-rootfs.vhd]({get_image_object_url(path['s3_bucket_name'], path['s3_key'])})\n"
    return output

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

def generate_package_update_section(version):
    repo_definition_url =\
    f"https://gitlab.com/gardenlinux/gardenlinux-package-build/-/raw/main/packages/{version}.yaml"

    output = ""
    with urllib.request.urlopen(repo_definition_url) as f:
        data = yaml.load(f.read().decode('utf-8'), Loader=SafeLoader)
        if data['version'] != version:
            print(f"ERROR: version string in {repo_definition_url} does not match {version}")
            sys.exit(1)
        for source in data['publish']['sources']:
            # excluded section does not contain release note information 
            if source['type'] == 'exclude':
                continue
            # base mirror does not contain packages specification
            if 'packages' not in source:
                continue
            # Only check packages lists if it contains a list of either matchSources or matchBinaries
            for s in source['packages']:
                if 'matchSources' in s:
                    output += _parse_match_section(s['matchSources'])
                if 'matchBinaries' in source['packages']:
                    output += _parse_match_section(s['matchBinaries'])
    return output

def release_notes_changes_section():
    return textwrap.dedent("""
    ## Changes
    The following packages have been upgraded, to address the mentioned CVEs:
    **todo release facilitator: fill this in**
    """)

def release_notes_software_components_section(package_list):
    output = "\n"
    output += "## Software Component Versions\n"
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
                output += subprocess.check_output(['/bin/bash','./hack/compare-apt-repo-versions.sh', previous_version, gardenlinux_version]).decode("utf-8")
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

def create_github_release_notes(gardenlinux_version, commitish, dry_run = False):
    commitish_short=commitish[:8]

    package_list = _get_package_list(gardenlinux_version)

    output = ""

    output += release_notes_changes_section()

    output += release_notes_software_components_section(package_list)

    output += release_notes_compare_package_versions_section(gardenlinux_version, package_list)

    manifests = download_all_singles(gardenlinux_version, commitish_short)

    output += generate_release_note_image_ids(manifests)

    output += "\n"
    output += "## Kernel Package direct download links\n"
    output += get_kernel_urls(gardenlinux_version)
    output += "\n"

    output += generate_image_download_section(manifests, gardenlinux_version, commitish_short )

    output += "\n"
    output += "## Kernel Module Build Container (kmodbuild) "
    output += "\n"
    output += "```"
    output += "\n"
    output += f"ghcr.io/gardenlinux/kmodbuild:{gardenlinux_version}"
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
        body = create_github_release_notes(args.tag, args.commit, args.dry_run)
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


# # Example usage
# try:
#     release_info = create_github_release('gardenlinux', 'gardenlinux', "1312.0", "40b9db2c")
#     print(release_info)
# except Exception as e:
#     print(f"Error occurred: {e}")
