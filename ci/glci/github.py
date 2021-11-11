import enum

import ccc.github


class GitHubStatus(enum.Enum):
    ERROR = 'error'
    FAILURE = 'failure'
    PENDING = 'pending'
    SUCCESS = 'success'


def post_github_status(
    github_cfg,
    committish: str,
    state: GitHubStatus,
    target_url: str = None,
    description: str = None,
    context: str = "tekton-pipelines",

):
    github_api = ccc.github.github_api(github_cfg)

    repo = github_api.repository(owner='gardenlinux', repository='gardenlinux')
    repo.create_status(
        sha=committish,
        state=state.value,
        target_url=target_url,
        description=description,
        context=context,
    )
