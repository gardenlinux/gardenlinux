"""
Ref: SRG-OS-000278-GPOS-00108

Verify the operating system uses cryptographic mechanisms to protect the
integrity of audit tools.
"""


def test_auditd_is_not_tampered(dpkg_checksums, shell):
    """
    Note: hashlib is not used here because its md5 functionality
          is not available with fips-enabled flavors.
    """
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
