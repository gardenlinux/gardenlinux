ARG base
FROM $base
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y aptitude ca-certificates dpkg-dev gh jq
RUN dpkg --add-architecture amd64 && dpkg --add-architecture arm64 && apt-get update
COPY fetch_releases download_pkgs create_dist /
