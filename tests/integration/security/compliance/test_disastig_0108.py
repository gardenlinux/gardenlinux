import hashlib

import pytest

"""
Ref: SRG-OS-000278-GPOS-00108

Verify the operating system uses cryptographic mechanisms to protect the
integrity of audit tools.
"""


def file_checksum(filepath):
    """
    usedforsecurity=False is needed to run in a FIPS environment
    """
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()


@pytest.mark.booted(reason="Requires working networking")
@pytest.mark.root(
    reason="Unloading crypto modules in dpkg_checksums plugin requires elevated permissions"
)
def test_auditd_is_not_tampered(dpkg, dpkg_checksums, shell):
    if not dpkg.package_is_installed("auditd"):
        return

    ideal_checksums = dpkg_checksums.for_package("auditd")
    for bin in ["auditd", "auditctl", "augenrules", "aureport", "ausearch"]:
        bin_path = f"/usr/sbin/{bin}"
        assert ideal_checksums[bin_path] == file_checksum(
            bin_path
        ), f"checksum of /usr/sbin/{bin} does not match the one from the corresponding deb package"
