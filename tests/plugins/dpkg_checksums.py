import os
import tempfile

import pytest


class DpkgChecksums:
    def __init__(self, shell):
        self._shell = shell

    def for_package(self, package_name, package_version="INSTALLED") -> dict:
        """
        We cannot trust md5sums files stored in /var/lib/dpkg/info,
        so we do not use debsums and instead
        we are fetching md5sums control file from a package in an apt repository.
        """
        if package_version == "INSTALLED":
            package_version = self._shell(
                f"dpkg-query -W -f='${{Version}}' {package_name}", capture_output=True
            ).stdout

        oldpwd = os.getcwd()

        with tempfile.TemporaryDirectory(delete=False) as td:
            os.chdir(td)

            self._shell(f"apt-get download {package_name}={package_version}")
            self._shell(f"dpkg-deb --control {package_name}*.deb")

            checksums = {
                f"/{path}": md5
                for line in open("DEBIAN/md5sums")
                for md5, path in [line.strip().split()]
            }

            os.chdir(oldpwd)

        return checksums


@pytest.fixture
def dpkg_checksums(shell) -> DpkgChecksums:
    return DpkgChecksums(shell)
