#!/usr/bin/env python3

# Generate Release Notes for a Garden Linux Release
#
# Example Usage:
#    ./<this script name>.py --version 934.6 --commitish 76ea662
#

import click
import os
import boto3
import yaml
import urllib.request
import sys
from yaml.loader import SafeLoader

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
        if pset == 'published_marketplace_images':
            output += "# all regions:\n"
            for market_image in published_image_metadata[pset]:
                output += f"Hyper V: {market_image['hyper_v_generation']}, "
                output += f"urn: {market_image['urn']}\n"
    return output


def construct_release_note_single(manifest_path):
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
    s3_client = boto3.client('s3')
    s3_client.download_file(bucket, remote_filename, local_filename)


def download_meta_single_manifest(bucket, bucket_path, image_name, dest_path):
    download_s3_file(bucket, f"{bucket_path}/{image_name}", f"{dest_path}/{image_name}")
    return f"{dest_path}/{image_name}"


def download_all_singles(bucket, path, version, commitish):

    local_dest_path = "s3_downloads"
    os.makedirs(local_dest_path, exist_ok=True)
    manifests = list()
    for a in arches:
        for p in cloud_fullname_dict:
            fname = construct_full_image_name(p, "gardener_prod", a, version, commitish)
            manifests.append(download_meta_single_manifest(bucket, path, fname, "s3_downloads/"))
    return manifests


def generate_publish_release_note_section(version, commitish):
    singles_path = "meta/singles"
    bucket = "gardenlinux-github-releases"
    manifests = download_all_singles(bucket, singles_path, version, commitish)
    out = ""
    for m in manifests:
        out += construct_release_note_single(m)
    return out


def _parse_match_section(pkg_list: list):
    output = ""
    for pkg in pkg_list:
        # If is dict, the package has additional information relevant for release notes
        if isinstance(pkg, dict):
            pkg_string = next(iter(pkg))
            output += f"{pkg_string}:\n"
            for item in pkg[pkg_string]:
                for k,v in item.items():
                    output += f"- {k}: {v}\n"
    return output

def generate_package_update_section(version):
    repo_definition_url =\
    f"https://gitlab.com/gardenlinux/gardenlinux-package-build/-/raw/main/packages/{version}.yaml"
    # test data with security note annotations:
    # "https://gitlab.com/gardenlinux/gardenlinux-package-build/-/raw/96f717072edf0c454e588e8bafa8d4419807a412/packages/934.6.yaml"
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


@click.command()
@click.option('--version', required=True)
@click.option('--commitish', required=False)
def generate(version, commitish):

    output = "## Package Updates\n"
    output += generate_package_update_section(version)
    output += "\n"
    output += "## Public cloud images\n"
    output += generate_publish_release_note_section(version, commitish)
    output += "\n"
    print(output)


if __name__ == '__main__':
    generate()
