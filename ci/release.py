#!/usr/bin/env python3

import argparse
import logging
import sys

import glci.github
import glci.util
import glci.model
import paths

logger = logging.getLogger(__name__)


def ensure_target_branch_exists(
    release_branch: str,
    release_committish: str,
    release_version: str,
    git_helper,
    giturl: str,
):
    major, minor = [int(vp) for vp in release_version.split('.')]

    is_first_release = minor == 0

    gh_repo = github.github_repo(giturl=giturl)
    repo = git_helper.repo

    release_branch_exists = release_branch in {b.name for b in gh_repo.branches()}
    logger.debug(f'{release_branch_exists=}')

    repo = git_helper.repo
    release_commit = repo.rev_parse(release_committish)
    logger.debug(f'{release_commit=}')

    if is_first_release:
        # release_branch MUST not exist, yet
        if release_branch_exists:
            logger.error(f'{release_branch=} already exists - aborting release')
            sys.exit(1)

        gh_repo.create_branch_ref(
            name=release_branch,
            sha=release_commit.hexsha,
        )
        logger.info(f'created new branch {release_branch=} pointing to {release_commit=}')
    else:
        # release_branch MUST exist
        if not release_branch_exists:
            logger.error(f'{release_branch=} does not exist - aborting patch-release')
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


def create_release(
        giturl: str,
        tag_name: str,
        target_commitish: str,
        body: str,
        draft: bool,
        prerelease: bool,
):
    gh_repo = glci.github.github_repo(giturl=giturl)
    release = gh_repo.create_release(
        target_commitish=target_commitish,
        tag_name=tag_name,
        body=body,
        draft=draft,
        prerelease=prerelease,
    )
    return release


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cicd-cfg', default='default')
    parser.add_argument(
        '--giturl',
        default='ssh://git@github.com/gardenlinux/gardenlinux'
    )
    parser.add_argument(
        '--release-version',
        default=glci.model.next_release_version_from_workingtree()[0],
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

    git_helper = github.git_helper(giturl=parsed.giturl)

    release_branch = release_branch_name(gardenlinux_epoch=gardenlinux_epoch)
    release_committish = parsed.release_committish

    logger.info(f'next release version: {release_version=}')

    ensure_target_branch_exists(
        release_committish=release_committish,
        release_branch=release_branch,
        release_version=release_version,
        git_helper=git_helper,
        giturl=parsed.giturl,
    )


if __name__ == '__main__':
    main()
