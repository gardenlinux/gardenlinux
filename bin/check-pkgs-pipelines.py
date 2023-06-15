#!/usr/bin/env python3

import argparse
import re
import requests
import re
import glob
from pprint import pprint

import yaml


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

    return sorted_report


def main(full):
   report = check_pkgs_pipelines(full)
   if report:
       print("Failed Gitlab Pipelines:")
       print(yaml.dump(dict(report)))
       exit(1)
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Check package availability')
    parser.add_argument("--full", help="include all projects, not just those with non-successful pipeline status", action="store_true")
    args = parser.parse_args()
    main(args.full)