import pytest

"""
Ref: SRG-OS-000278-GPOS-00108

Verify the operating system uses cryptographic mechanisms to protect the
integrity of audit tools.
"""


@pytest.mark.booted(reason="Requires working networking")
@pytest.mark.root(
    reason="Unloading crypto modules in dpkg_checksums plugin requires elevated permissions"
)
def test_auditd_is_not_tampered(dpkg_checksums, shell):
    checksums = dpkg_checksums.for_package("auditd")
    for bin in ["auditd", "auditctl", "augenrules", "aureport", "ausearch"]:
        ideal_checksum = checksums[f"/usr/sbin/{bin}"]
        on_disk_checksum = (
            shell(f"md5sum /usr/sbin/{bin}", capture_output=True)
            .stdout.strip()
            .split()[0]
        )
        assert (
            ideal_checksum == on_disk_checksum
        ), f"checksum of /usr/sbin/{bin} does not match the one from the corresponding deb package"
