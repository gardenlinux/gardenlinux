import pytest

"""
Ref: SRG-OS-000278-GPOS-00108

Verify the operating system uses cryptographic mechanisms to protect the
integrity of audit tools.
"""


@pytest.mark.booted(reason="Requires working networking")
def test_auditd_is_not_tampered(dpkg, dpkg_checksums, shell):
    if not dpkg.package_is_installed("auditd"):
        return

    ideal_checksums = dpkg_checksums.for_package("auditd")
    for bin in ["auditd", "auditctl", "augenrules", "aureport", "ausearch"]:
        assert dpkg_checksums.is_matching_with_installed(
            ideal_checksums, f"/usr/sbin/{bin}"
        ), f"checksum of /usr/sbin/{bin} does not match the one from the corresponding deb package's md5sums control file"
