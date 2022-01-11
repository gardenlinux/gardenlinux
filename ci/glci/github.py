import enum

import ccc.github
import gitutil
import paths
import urllib


class GitHubStatus(enum.Enum):
    ERROR = 'error'
    FAILURE = 'failure'
    PENDING = 'pending'
    SUCCESS = 'success'


def github_cfg(giturl: str):
    repo_url = urllib.parse.urlparse(giturl)
    github_cfg = ccc.github.github_cfg_for_hostname(
        repo_url.hostname,
    )
    return github_cfg


def git_helper(
    giturl: str,
):
    cfg = github_cfg(giturl=giturl)
    repo_url = urllib.parse.urlparse(giturl)

    repo_url = urllib.parse.urlparse(giturl)
    repo_path = repo_url.path

    return gitutil.GitHelper(
        repo=paths.repo_root,
        github_cfg=cfg,
        github_repo_path=repo_path,
    )


def github_repo(
    giturl: str,
):
    repo_url = urllib.parse.urlparse(giturl)
    cfg = github_cfg(giturl=giturl)
    org, repo = repo_url.path.strip('/').split('/')
    repo = repo.removesuffix('.git')

    github_api = ccc.github.github_api(cfg)

    gh_repo = github_api.repository(owner=org, repository=repo)

    return gh_repo


def post_github_status(
    git_url: str,
    committish: str,
    state: GitHubStatus,
    target_url: str = None,
    description: str = None,
    context: str = "tekton-pipelines",

):
    repo = github_repo(giturl=git_url)

    repo.create_status(
        sha=committish,
        state=state.value,
        target_url=target_url,
        description=description,
        context=context,
    )
