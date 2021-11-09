import base64
import os
import urllib.parse

import git

import ccc.github
import distutils.util
import gitutil


def apply_patch(
        repo_dir: str,
):
    patch = PATCH_CONTENT # global variable rendered at runtime
    patch_decoded = base64.b64decode(patch.encode('utf-8'))
    patch_decoded = patch_decoded.decode('utf-8')

    patch_path = os.path.join(repo_dir, 'gardenlinux.patch')
    with open(patch_path, 'w') as f:
        f.write(patch_decoded)

    repo = git.Repo(repo_dir)
    git_cli = repo.git
    patch = git_cli.apply(patch_path, '--whitespace=nowarn')
    os.unlink(patch_path)


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


def prepare_home_dir():
    if home_dir := os.environ.get('HOME'):
        print(f"Preparing HOME at '{home_dir}'")
        os.makedirs(os.path.abspath(home_dir), exist_ok=True)


def clone_and_copy(
    giturl: str,
    committish: str,
    repo_dir: str,
):
    repo_dir = os.path.abspath(repo_dir)
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

    prepare_home_dir()

    print(f'cloned to {repo_dir=} {commit_hash=}')
    print(f'Commit Message: {commit_msg}')

    if PATCH_CONTENT:
        print("Applying patch containing all diffs against remote")
        apply_patch(repo_dir=repo_dir)
