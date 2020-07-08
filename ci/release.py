#!/usr/bin/env python3

import argparse
import urllib.parse
import sys

import ccc.github
import gitutil

import glci.util
import glci.model
import paths


def _github_cfg(giturl: str):
    repo_url = urllib.parse.urlparse(giturl)
    github_cfg = ccc.github.github_cfg_for_hostname(
        repo_url.hostname,
    )
    return github_cfg


def _git_helper(
    giturl: str,
):
    github_cfg = _github_cfg(giturl=giturl)
    repo_url = urllib.parse.urlparse(giturl)

    repo_url = urllib.parse.urlparse(giturl)
    repo_path = repo_url.path

    return gitutil.GitHelper(
        repo=paths.repo_root,
        github_cfg=github_cfg,
        github_repo_path=repo_path,
    )


def _github_repo(
    giturl: str,
):
    repo_url = urllib.parse.urlparse(giturl)
    github_cfg = _github_cfg(giturl=giturl)
    org, repo = repo_url.path.strip('/').split('/')

    github_api = ccc.github.github_api(github_cfg)

    gh_repo = github_api.repository(owner=org, repository=repo)

    return gh_repo


def ensure_target_branch_exists(
    release_branch: str,
    release_committish: str,
    release_version: str,
    git_helper,
    giturl: str,
):
    major, minor = [int(vp) for vp in release_version.split('.')]

    is_first_release = minor == 0

    gh_repo = _github_repo(giturl=giturl)
    repo = git_helper.repo

    release_branch_exists = release_branch in {b.name for b in gh_repo.branches()}
    print(f'{release_branch_exists=}')

    if is_first_release:
        # release_branch MUST not exist, yet
        if release_branch_exists:
            print(f'Error: {release_branch=} already exists - aborting release')
            sys.exit(1)

        repo = git_helper.repo
        release_commit = repo.rev_parse(release_committish)
        print(f'{release_commit=}')

        gh_repo.create_branch_ref(
            name=release_branch,
            sha=release_commit.hexsha,
        )
        print(f'created new branch {release_branch=} pointing to {release_commit=}')
    else:
        # release_branch MUST exist
        if not release_branch_exists:
            print(f'Error {release_branch=} does not exist - aborting patch-release')
            sys.exit(1)

    # stamp tag + create release + create bump-commit
    next_release_version = f'{major}.{minor + 1}'

    with open(paths.version_path, 'w') as f:
        f.write(next_release_version)

    bump_commit = git_helper.index_to_commit(
        message=f'prepare release of gardenlinux-{next_release_version}',
        parent_commits=(release_commit,)
    )

    git_helper.push(
        from_ref=bump_commit.hexsha,
        to_ref=release_branch,
    )


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument(
        '--giturl',
        default='ssh://git@github.com/gardenlinux/gardenlinux'
    )
    parser.add_argument(
        '--release-version',
        default=glci.model.next_release_version_from_workingtree(),
    )
    parser.add_argument(
        '--release-committish',
        required=True,
    )
    parsed = parser.parse_args()

    return parsed


def release_branch_name(gardenlinux_epoch):
    return f'rel-{gardenlinux_epoch}'


def main():
    parsed = parse_args()

    release_version = parsed.release_version
    gardenlinux_epoch = int(release_version.split('.')[0])

    git_helper = _git_helper(giturl=parsed.giturl)

    release_branch = release_branch_name(gardenlinux_epoch=gardenlinux_epoch)
    release_committish = parsed.release_committish

    print(f'next release version: {release_version=}')

    ensure_target_branch_exists(
        release_committish=release_committish,
        release_branch=release_branch,
        release_version=release_version,
        git_helper=git_helper,
        giturl=parsed.giturl,
    )


if __name__ == '__main__':
    main()
