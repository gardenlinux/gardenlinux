#!/usr/bin/env python3

import argparse
import re
import requests
import re
import glob
from pprint import pprint

import yaml

def read_pkg_files(arch):
    regex_package='echo ([\w-]+)'
    regex_arch='arch=([\w-]+)'
    packages = []

    for filename in glob.glob('features/*/pkg.include'):
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if not line:
                    continue
                if line.startswith("$(if"):
                    # If line matches '$(if', then extract the package name
                    match_pkg = re.search(regex_package, line)
                    match_arch = re.search(regex_arch, line)
                    if match_pkg and match_arch and match_arch.group(1) == arch:
                        package_name = match_pkg.group(1).replace('$arch', arch)
                        packages.append(package_name)
                else:
                    package_name = line.replace('$arch', arch)
                    packages.append(package_name)

    return packages

def get_available_pkgs_from_repo(url) -> list():
    response = requests.get(url)
    response.raise_for_status()

    packages = []
    for line in response.text.split('\n'):
        match = re.match(r'^Package: ([\w.-]+)', line)
        if match:
            packages.append(match.group(1))

    return packages

def get_unavailable_packages(available_packages, required_packages):
    unavailable_packages = set(required_packages) - set(available_packages)
    return list(unavailable_packages)


def check_packages(arch, dist) -> list():
    available_packages = get_available_pkgs_from_repo(f"https://repo.gardenlinux.io/gardenlinux/dists/{dist}/main/binary-{arch}/Packages")
    required_packages = read_pkg_files(arch)
    missing_packages = get_unavailable_packages(available_packages, required_packages)
    return missing_packages


def check_pkgs_pipelines(full=False):
    gitlab_url = 'https://gitlab.com'
    group_name = 'gardenlinux'

    response = requests.get(f'{gitlab_url}/api/v4/groups/{group_name}', headers="")
    group_id = response.json()['id']

    response = requests.get(f'{gitlab_url}/api/v4/groups/{group_id}/projects?visibility=public', headers="")
    projects = response.json()

    report = {}

    for project in projects:
        if project['archived']:
            continue

        project_id = project['id']
        last_activity_at = project['last_activity_at']
        project_web_url = project['web_url']

        response = requests.get(f'{gitlab_url}/api/v4/projects/{project_id}/pipelines?ref=main', headers="")
        pipelines = response.json()

        if pipelines:
            pipeline_status = pipelines[0]['status']
        else:
            pipeline_status = None

        if not full and pipeline_status == 'success':
            continue

        # Get open issues
        response = requests.get(f'{gitlab_url}/api/v4/projects/{project_id}/issues?state=opened', headers="")
        open_issues = len(response.json())

        # Use the project name as the key, and the value is another dict containing the information for that project
        report[project['name']] = {
            'last_activity_at': last_activity_at,
            'pipeline_status': pipeline_status,
            'web_url': project_web_url,
            'open_issues': open_issues,
        }

    sorted_report = sorted(report.items(), key=lambda x: x[1]['pipeline_status'] != 'failed', )

    if sorted_report:
        print(yaml.dump(dict(sorted_report)))
    else:
        print("None")


def main(dist):
    for arch in ["arm64", "amd64"]:

        missing_packages = check_packages(arch, dist)
        if missing_packages:
            print(f"Missing Packages ({arch}):")
            pprint(missing_packages)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check package availability')
    parser.add_argument('-d', '--dist', required=True, help='Distribution of the apt repository (e.g. today for gardenlinux repo)')
    args = parser.parse_args()
    main(args.dist)