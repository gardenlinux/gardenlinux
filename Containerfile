ARG base
FROM $base
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y aptitude ca-certificates dpkg-dev gh jq
COPY fetch_releases download_pkgs create_dist /
