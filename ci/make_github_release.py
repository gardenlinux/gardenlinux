#!/usr/bin/env python3

import github_release

"""
This script can be used to manually create a Github release page (draft-release).
This is useful for hotfix-releases on older branches (576 and before) where the automation was
not yet in place.
Instructions:
* Change the parameters from below according to the current release
* Checkout branch 'main' (!) from the Gardenlinux Git repo
* Open a shell and cd to the folder 'ci'
* Run python3 ./make_gh_release.py

This script needs a proper development environment to be executed. Ensure that:
* you have the necessary environment variables set
* you have a Python virtual environment with all requirements, see also
    images/step_image/requirements.txt
"""


def main():
    # usually not changed
    cicd_cfg_name = 'default'
    ctx_repository_config_name = 'gardener-dev'
    flavour_set_name = 'all'
    git_url = 'https://github.com/gardenlinux/gardenlinux.git'

    # change these parameters according to the release to be published:
    gardenlinux_epoch = '576'
    committish = 'c7bb2e0f81d8bd8bdbad6b1229ed21da586e027c'
    repo_dir = '<your local Git working dir>'
    version = '576.3'

    github_release.make_release(
        cicd_cfg_name=cicd_cfg_name,
        committish=committish,
        ctx_repository_config_name=ctx_repository_config_name,
        flavour_set_name=flavour_set_name,
        gardenlinux_epoch=gardenlinux_epoch,
        giturl=git_url,
        repo_dir=repo_dir,
        version=version,
    )


if __name__ == '__main__':
    main()
