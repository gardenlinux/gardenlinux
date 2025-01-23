# Dependency management via Dependabot
# this is really hackish

FROM ghcr.io/gardenlinux/builder:191279b0a54c227851413077283c69df29ce7335 AS oldbuilder

FROM ghcr.io/gardenlinux/builder:9e4906f911c476916d3b6010dc37436b9fa621c6
RUN rm -rf /builder && apt-get update && apt-get install -y --no-install-recommends debootstrap
COPY --from=oldbuilder /builder /builder
RUN sed 's|--keyring "$keyring" --arch|--keyring /builder/key/key.asc --arch|g' -i /builder/bootstrap
