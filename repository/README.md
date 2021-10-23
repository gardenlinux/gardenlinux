The repo is originally configured without a GPG Key.

setting the gpg key to the repo, after it is being set there is no need to modify it as it is saved in conf/distributions and will always be used

    ./repo.sh --gpg-key="DEADBEEF" --set-key 

download is going to go over all packages defined in packages_debian, calculate the dependencies and download the packages and sources

    ./repo.sh --download

this is going to add all packages/sources to the repository

    ./repo.sh --publish
