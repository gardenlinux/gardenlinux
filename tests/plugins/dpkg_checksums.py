import hashlib
import os
import tempfile
from shutil import chown

import pytest


class DpkgChecksums:
    def __init__(self, shell):
        self._shell = shell

    def for_package(self, package_name, package_version="INSTALLED") -> dict:
        """
        Returns a dict of filepath => md5sum (as recorded in a package's
        md5sums control file).
        As we cannot trust md5sums files stored in /var/lib/dpkg/info, we do
        not use debsums and instead this code fetches md5sums control file from
        a package in an apt repository.
        """
        if package_version == "INSTALLED":
            package_version = self._shell(
                f"dpkg-query -W -f='${{Version}}' {package_name}", capture_output=True
            ).stdout

        oldpwd = os.getcwd()

        with tempfile.TemporaryDirectory(delete=False) as td:
            uid, _ = self._shell.user
            chown(td, uid)

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

    def is_matching_with_installed(self, package_checksums, file_on_disk_path) -> bool:
        """
        Compares an md5 checksum of a file on disk with the one from package's
        md5sums control file.

        usedforsecurity=False is needed to run in a FIPS environment
        """
        with open(file_on_disk_path, "rb") as f:
            real_checksum = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
            return real_checksum == package_checksums[file_on_disk_path]


@pytest.fixture
def dpkg_checksums(shell, kernel_module):
    # if some of the modules were already loaded before we've done anything here,
    # do not attempt to unload them once the work is done
    # crypto_modules = ["crypto_user", "algif_hash", "af_alg"]
    # modules_to_cleanup = [
    #     m for m in crypto_modules if not kernel_module.is_module_loaded(m)
    # ]

    yield DpkgChecksums(shell)

    # for m in modules_to_cleanup:
    #     kernel_module.unload_module(m)
