# Dependency management via Dependabot

FROM ghcr.io/gardenlinux/builder:191279b0a54c227851413077283c69df29ce7335

RUN curl -sSLf https://github.com/gardenlinux/seccomp_fake_xattr/releases/download/latest/seccomp_fake_xattr-$(uname -m).tar.gz \
	| gzip -d \
	| tar -xO seccomp_fake_xattr-$(uname -m)/fake_xattr > /usr/bin/fake_xattr \
	&& chmod +x /usr/bin/fake_xattr
