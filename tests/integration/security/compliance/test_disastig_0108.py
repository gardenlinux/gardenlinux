import hashlib

"""
Ref: SRG-OS-000278-GPOS-00108

Verify the operating system uses cryptographic mechanisms to protect the
integrity of audit tools.
"""


def _checksum_file(filepath):
    h = hashlib.md5()

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def test_auditd_is_not_tampered(dpkg):
    for bin in ["auditd", "auditctl", "augenrules", "aureport", "ausearch"]:
        ideal_checksum = dpkg.package_files_checksums("auditd")[f"/usr/sbin/{bin}"]
        assert ideal_checksum == _checksum_file(
            f"/usr/sbin/{bin}"
        ), f"checksum of /usr/sbin/{bin} does not match the one from the corresponding deb package"
