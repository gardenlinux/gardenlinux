import logging

import git

logger = logging.getLogger(__name__)


def git_clone(
    git_url: str,
    committish: str,
    working_dir: str,
):

    repo = git.Repo.clone_from(git_url, working_dir)
    repo.git.checkout(committish)

    logger.info(f'cloned to {working_dir=} {repo.head.commit.hexsha=}')
    logger.info(f'Commit Message: {repo.head.commit.message}')

    return repo.head.commit.message, repo.head.commit.hexsha


def dummy():
    pass
