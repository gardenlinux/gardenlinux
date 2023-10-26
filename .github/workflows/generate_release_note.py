#!/usr/bin/env python3

# This is currently not part of the automated pipeline. A garden linux maintainer must execute this locally
# # install python dependencies 
# python3 -m venv venv
# source venv/bin/activate
# pip install boto3 pyyaml
# # Execute the command (example for 934.10):
# .github/workflows/generate_release_note.py generate --version 934.10 --commitish f057c9b 

import os
import boto3
import botocore
import yaml
import urllib.request
import sys
from yaml.loader import SafeLoader
import argparse
import subprocess

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
    if commitish == None:
        raise Exception("Commitish is not set")
    local_dest_path = "s3_downloads"
    os.makedirs(local_dest_path, exist_ok=True)
    manifests = list()
    for a in arches:
        for p in cloud_fullname_dict:
            fname = construct_full_image_name(p, "gardener_prod", a, version, commitish)
            try:
                manifests.append(download_meta_single_manifest(bucket, path, fname, "s3_downloads/"))
            except Exception as e:
                print(f"Failed to get manifest. Error: {e}")
                print(f"\tfname:{fname}")
                print(f"\tfname:{path}")

    return manifests


def generate_publish_release_note_section(manifests):
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

def generate_image_readme():
    output = ""
    output += '''<details>
## How to import images to public Cloud Providers

- Alibaba Cloud
    - [Import custom images](https://www.alibabacloud.com/help/doc-detail/25464.htm) to Alibaba Cloud

- AWS
    - [Importing an Image into Your Device as an Amazon EC2 AMI](https://docs.aws.amazon.com/snowball/latest/developer-guide/ec2-ami-import-cli.html)
    - recommended `aws` command with parameters:
      ```shell
      aws ec2 register-image --name gardenlinux --description "Garden Linux" --architecture x86_64 --root-device-name /dev/xvda --virtualization-type hvm --ena-support --block-device-mapping "DeviceName=/dev/xvda,Ebs={DeleteOnTermination=True,SnapshotId=<your snapshot ID from snapshot import>,VolumeType=gp2}"
      ```

- Google Cloud Platform
    - [Importing a bootable virtual disk](https://cloud.google.com/compute/docs/import/importing-virtual-disks#bootable) to GCP

- Microsoft Azure
    - [Bringing and creating Linux images in Azure](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/imaging)

</details>'''

    return output


def get_image_object_url(bucket, object, expiration=0):
    s3_config = botocore.config.Config(signature_version=botocore.UNSIGNED)
    s3_client = boto3.client('s3', config=s3_config)
    url = s3_client.generate_presigned_url('get_object', Params={'Bucket': bucket, 'Key': object}, ExpiresIn = expiration)
    return url


def main():
    parser = argparse.ArgumentParser(description="Command Line Interface", add_help=False)
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    generate_package_notes_parser = subparsers.add_parser('generate_package_notes', help='Only generates Package Updates Section')
    generate_package_notes_parser.add_argument('--version', required=True, help='Target Garden Linux Version')

    generate_publish_notes_parser = subparsers.add_parser('generate_publish_notes', help='Only generates publishing info section')
    generate_publish_notes_parser.add_argument('--version', required=True, help='Target Garden Linux Version')
    generate_publish_notes_parser.add_argument('--commitish', required=True, help='commitish used by publishing pipeline. required to download respective manifests')

    generate_parser = subparsers.add_parser('generate', help='Generates full release notes')
    generate_parser.add_argument('--version', required=True, help='Target Garden Linux Version')
    generate_parser.add_argument('--commitish', required=True, help='commitish used by publishing pipeline. required to download respective manifests')

    args = parser.parse_args()

    singles_path = "meta/singles"
    bucket = "gardenlinux-github-releases"
    if args.cmd == "generate_package_notes":
        generate_package_notes(args.version)

    elif args.cmd == "generate_publish_notes":
        manifests = download_all_singles(bucket, singles_path, args.version, args.commitish)
        generate_publish_notes(manifests)

    elif args.cmd == "generate":
        manifests = download_all_singles(bucket, singles_path, args.version, args.commitish)
        generate(args.version, args.commitish, manifests)

def generate_package_notes(version):
    output = "## Package Updates\n"
    output += generate_package_update_section(version)
    output += "\n"
    print(output)

def generate_publish_notes(manifests):
    output = "## Public cloud images\n"
    output += generate_publish_release_note_section(manifests)
    output += "\n"
    print(output)

def generate(version, commitish, manifests):
    output = "## Package Updates\n"
    output += generate_package_update_section(version)
    output += "\n"
    output += "## Public cloud images\n"
    output += generate_publish_release_note_section(manifests)
    output += "\n"
    output += "## Pre-built images available for download\n"
    output += generate_image_download_section(manifests, version, commitish)
    output += "\n"
    output += generate_image_readme()
    output += "\n"
    output += "## Kernel URLs\n"
    output += "```yaml\n"
    output += subprocess.run(["bin/gl-kernelurls", "-g", version, "-a", "arm64", "-a", "amd64"], capture_output=True).stdout.decode('UTF-8')
    output += "```"
    output += "\n"
    print(output)



if __name__ == '__main__':
    main()