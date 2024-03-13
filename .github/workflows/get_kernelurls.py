#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import requests
import lzma
import gzip
import json
import yaml
import itertools

def get_pkg_attr(package_name, attribute_key, packages_per_repo):
  
    current_package = {}
    found_package = False
    for packages in packages_per_repo.values():
       for line in packages.split('\n'):
            # Check for new package section or end of file
            if line.startswith("Package: ") or line.strip() == "":
                if found_package:
                    # Return the attribute if it exists
                    return current_package.get(attribute_key)
                current_package = {}
                found_package = False

            key_value = line.split(": ", 1)
            if len(key_value) == 2:
                key, value = key_value
                current_package[key.strip()] = value.strip()

            # Check if current section is the desired package
            if current_package.get("Package") == package_name:
                found_package = True


def get_kernel_urls(gardenlinux_version):
    if not gardenlinux_version:
        print("You need to specify gardenlinux_version")
    repositories = [f'http://packages.gardenlinux.io/gardenlinux {gardenlinux_version} main']

    architecture = ["arm64", "amd64"]
    versions = []
    packages = get_package_list(repositories, architecture)

    # find all Linux kernel versions available for the specified Gardenlinux version

    # We want to only list the packages for the specific kernel used for a given release
    # GL uses always the latest available kernel in the given repo, even if older kernel versions would be available.
    # Ideally we would parse the version of the package linux-headers-${arch}, which specifies the actual version.
    # Here, it is safe enough for the release notes to take the highest version available.
    latest_version = get_pkg_attr("linux-headers-amd64", "Version", packages)
    package_urls = check_urls([latest_version], get_package_urls(packages, 'linux-headers'), architecture)
    return output_urls(package_urls)

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

def output_urls(package_urls):

    yaml_output = "```yaml\n"
    yaml_output += ""
    yaml_output += yaml.dump(package_urls)
    yaml_output += "```\n"
    yaml_output += ""
    return yaml_output   
