FROM debian:testing-slim

RUN apt-get update && \
    apt-get install -y reprepro gpg libgpgme11 && \
    gpg --list-keys && \
    rm -rf /var/lib/apt/lists
