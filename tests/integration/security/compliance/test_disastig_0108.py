import pytest

"""
Ref: SRG-OS-000278-GPOS-00108

Verify the operating system uses cryptographic mechanisms to protect the
integrity of audit tools.
"""


@pytest.mark.feature("not fips")
def test_auditd_is_not_tampered(dpkg, shell):
    for bin in ["auditd", "auditctl", "augenrules", "aureport", "ausearch"]:
        ideal_checksum = dpkg.package_files_checksums("auditd")[f"/usr/sbin/{bin}"]
        on_disk_checksum = shell(f"md5sum /usr/sbin/{bin}", capture_output=True)
        assert (
            ideal_checksum == on_disk_checksum
        ), f"checksum of /usr/sbin/{bin} does not match the one from the corresponding deb package"
