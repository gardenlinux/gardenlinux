import os
import urllib.parse
import shutil

import ccc.github
import gitutil


def clone_and_copy(
    giturl: str,
    committish: str,
    repodir: str,
):
    repo_dir = os.path.abspath(repodir)
    repo_url = urllib.parse.urlparse(giturl)
    github_cfg = ccc.github.github_cfg_for_hostname(
      repo_url.hostname,
    )
    git_helper = gitutil.GitHelper.clone_into(
      target_directory=repo_dir,
      github_cfg=github_cfg,
      github_repo_path=repo_url.path,
    )
    git_helper.repo.git.checkout(committish)

    print(f'cloned to {repo_dir=}')
