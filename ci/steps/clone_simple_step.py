
import git


def git_clone(
    git_url: str,
    committish: str,
    working_dir: str,
):

    repo = git.Repo.clone_from(git_url, working_dir)
    repo.git.checkout(committish)

    print(f'cloned to {working_dir=} {repo.head.commit.hexsha=}')
    print(f'Commit Message: {repo.head.commit.message}')

    return repo.head.commit.message, repo.head.commit.hexsha


def dummy():
    pass
