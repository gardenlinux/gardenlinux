import urllib.parse

import ccc.github
import glci.github


def update_status(
    giturl: str,
    committish: str,
    namespace: str,
    pipeline_run_name: str,
):
    dashboard_url = (
        f'https://tekton-dashboard.gardenlinux.io/#/namespaces/{namespace}'
        f'/pipelineruns/{pipeline_run_name}'
    )
    repo_url = urllib.parse.urlparse(giturl)
    github_cfg = ccc.github.github_cfg_for_hostname(
        repo_url.hostname,
    )

    glci.github.post_github_status(
        github_cfg=github_cfg,
        committish=committish,
        target_url=dashboard_url,
        state=glci.github.GitHubStatus.PENDING,
        description='Pipeline run started',
    )
