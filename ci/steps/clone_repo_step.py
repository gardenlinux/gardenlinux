import os
import urllib.parse

import git

import ccc.github
import gitutil


def clone_and_checkout_with_technical_user(
    github_cfg,
    committish: str,
    repo_dir: str,
    repo_path: str,
):
    git_helper = gitutil.GitHelper.clone_into(
        target_directory=repo_dir,
        github_cfg=github_cfg,
        github_repo_path=repo_path,
    )
    repo = git_helper.repo
    repo.git.checkout(committish)

    return repo.head.commit.message, repo.head.commit.hexsha


def clone_and_checkout_anonymously(
    git_url,
    committish,
    repo_dir,
):
    if '://' not in git_url:
        parsed = urllib.parse.urlparse('x://' + git_url)
    else:
        parsed = urllib.parse.urlparse(git_url)

    url = f'https://{parsed.netloc}{parsed.path}'

    repo = git.Repo.clone_from(url, repo_dir)
    repo.git.checkout(committish)

    return repo.head.commit.message, repo.head.commit.hexsha


def clone_and_copy(
    giturl: str,
    committish: str,
    repodir: str,
):
    repo_dir = os.path.abspath(repodir)
    repo_url = urllib.parse.urlparse(giturl)

    try:
        github_cfg = ccc.github.github_cfg_for_hostname(
          repo_url.hostname,
        )
        commit_msg, commit_hash = clone_and_checkout_with_technical_user(
            github_cfg=github_cfg,
            committish=committish,
            repo_dir=repo_dir,
            repo_path=repo_url.path,
        )
    except ValueError:
        if repo_url.hostname == 'github.com':
            commit_msg, commit_hash = clone_and_checkout_anonymously(
                git_url=giturl,
                committish=committish,
                repo_dir=repo_dir,
            )
        else:
            raise RuntimeError(f"Unable to clone {giturl}")

    print(f'cloned to {repo_dir=} {commit_hash=}')
    print(f'Commit Message: {commit_msg}')


def cfssl_clone(
    cfssl_git_url: str,
    cfssl_committish: str,
    cfssl_dir: str,
):

    clone_and_copy(cfssl_git_url, cfssl_committish, cfssl_dir)