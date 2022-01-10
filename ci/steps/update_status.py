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

    glci.github.post_github_status(
        git_url=giturl,
        committish=committish,
        target_url=dashboard_url,
        state=glci.github.GitHubStatus.PENDING,
        description='Pipeline run started',
    )
