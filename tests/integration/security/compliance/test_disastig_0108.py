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
    """
    On a FIPS-enabled system MD5 algos are not available
    both for a python distribution used for testing and for a cli md5sum.
    md5 module in perl works though because it switches to a pure-perl
    algo implementation if its binary version fails to load.
    see: https://perldoc.perl.org/Digest::MD5.txt
    """
    checksums = dpkg_checksums.for_package("auditd")
    for bin in ["auditd", "auditctl", "augenrules", "aureport", "ausearch"]:
        ideal_checksum = checksums[f"/usr/sbin/{bin}"]
        on_disk_checksum = (
            shell(
                f"perl -e 'use Digest::MD5; print Digest::MD5::md5_hex(do {{ local $/; <STDIN> }}), \"\n\"' < /usr/sbin/{bin}",
                capture_output=True,
            )
            .stdout.strip()
            .split()[0]
        )
        assert (
            ideal_checksum == on_disk_checksum
        ), f"checksum of /usr/sbin/{bin} does not match the one from the corresponding deb package"
