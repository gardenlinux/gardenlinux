#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import requests
import lzma
import gzip
import argparse
import platform
import json
import yaml
import itertools

def main(args=None):
    parser = argparse.ArgumentParser(prog='gl-kernelurls', description='Output URLs to the kernel headers and its dependencies.')
    parser.add_argument('-g', '--gardenlinux', default='today',
                        help='Get Linux kernel package urls for a specific Gardenlinux version.')
    parser.add_argument('-o', '--output', choices=['yaml', 'json'], default='yaml', help='Select output format.')

    repositories = [f'https://repo.gardenlinux.io/gardenlinux {args.gardenlinux} main']

    if not args:
        args = parser.parse_args()

    architecture = ["arm64", "amd64"]
    versions = []
    packages = get_package_list(repositories, architecture)

    # find all Linux kernel versions available for the specified Gardenlinux version
    if args.gardenlinux:
        for package_list in packages.values():
            for package in package_list.split('\n'):
                if 'linux-headers' in package:
                    ex_version = ''
                    ex_version = re.match(".*/linux-headers-(\d.*-gardenlinux).*", package)
                    if ex_version:
                        versions.append(ex_version.group(1))
        versions = list(dict.fromkeys(versions))

    package_urls = check_urls(versions, get_package_urls(packages, 'linux-headers'), architecture)
    return output_urls(package_urls, args.output)

def get_repositories():
    '''Extract repositories url from /etc/apt/source.list and /etc/apt/source.list.d/*.
    '''
    repository_files = ['/etc/apt/sources.list']
    for file in os.listdir('/etc/apt/sources.list.d'):
        repository_files.append(f'/etc/apt/sources.list.d/{file}')

    repositories = []
    for repository_file in repository_files:
        with open(repository_file, 'r') as file:
            for line in file:
                if line.startswith('deb '):
                    repo = re.match(".*(http.*|ftp.*|file.*)", line).group(1)
                    repositories.append(repo)

    return repositories

def get_package_list(repositories, architecture):
    '''Get Packages lists from repository and return it as dictionary.
    '''
    packages_dict = {}
    for repo in repositories:
        repo_entries = repo.split(' ')
        uri = repo_entries[0]
        suite = repo_entries[1]
        for component, arch, compression in itertools.product(repo_entries[2:], ['all'] + architecture, ['.gz', '.xz', '']):
            packages_url = f'{uri}/dists/{suite}/{component}/binary-{arch}/Packages{compression}'
            response = requests.get(packages_url)
            if response.status_code == 200:
                if compression == '.xz':
                    packages = lzma.decompress(response.content).decode("UTF-8")
                elif compression == '.gz':
                    packages = gzip.decompress(response.content).decode("UTF-8")
                else:
                    packages = response.content.decode("UTF-8")

            packages_dict.update({f'{uri}-{suite}-{component}-{arch}': packages})

    return packages_dict

def get_package_urls(package_list, package_name, resolve_depends=True):
    '''Check if kernel headers and their dependencies are available. Returns a list
    with the complete urls to all found kernel header packages and their dependencies.
    '''
    header_packages = []
    dependencies = []
    for repo, packages in package_list.items():
        uri = re.match('(.*?)-.*', repo).group(1)
        for line in packages.split('\n'):
            if resolve_depends and line.startswith('Depends:'):
                dependencies = re.sub(' ?\(.*?\),?|,', '', re.match("Depends: (.*)", line).group(1)).split(' ')
            if line.startswith('Filename:') and f'/{package_name}' in line:
                filename = re.match("Filename: (.*)", line).group(1)
                header_packages.append(f'{uri}/{filename}')
                if resolve_depends:
                    for dependency in dependencies:
                        header_packages.extend(get_package_urls(package_list, dependency, False))

    return header_packages


def check_urls(linux_versions, header_package_urls, architecture):
    '''Pick the package urls that match the Linux image versions.
    '''
    result = {}
    versions = {}
    for arch, version in itertools.product(architecture, linux_versions):
        if not arch in result:
            result[arch] = {}
        result[arch][version] = []
    for version, arch, package in itertools.product(linux_versions, architecture, header_package_urls):
        if version in package and arch in package:
            result[arch][version].append(package)
            versions[version] = re.match(".*?(_.*)\.deb", package).group(1)
        # Workaround for linux compiler package name on arm64 architecture
        if 'arm64' in package and arch == 'arm64' and re.match('.*/gcc-\d\d_.*', package):
            result[arch][version].append(package)
    for version, arch, package in itertools.product(versions, architecture, header_package_urls):
        if versions[version] in package and arch in package and not 'linux-headers' in package:
            result[arch][version].append(package)
    
    for key, value in result.items():
        for nested_key, nested_value in value.items():
            result[key][nested_key] = list(dict.fromkeys(nested_value))

    return result

def output_urls(package_urls, output):
    '''Output the urls in a usable format.
    '''
    if output == 'json':
        return json.dumps(package_urls)
    elif output == 'yaml':
        yaml_output = yaml.dump(package_urls)
        return yaml_output   
    else:
        print('Invalid output format, choose `json` or `yaml`.')

if __name__ == "__main__":
    main()