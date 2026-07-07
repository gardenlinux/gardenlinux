"""
Ref: SRG-OS-000255-GPOS-00096

Verify the operating system produces audit records containing information to
establish the identity of any individual or process associated with the event.
"""

import re

import pytest


@pytest.mark.security_id(203671)
@pytest.mark.feature("not container and not lima")
@pytest.mark.booted(reason="audit retention validation requires audit subsystem")
@pytest.mark.root(reason="required to read audit configuration and logs")
def test_audit_records_contain_identity_information(shell):
    """Verify audit records carry identity fields (auid, uid, pid, comm, exe)."""
    result = shell(
        "ausearch -ts recent",
        capture_output=True,
        ignore_exit_code=True,
    )

    stdout = result.stdout or ""

    identity_patterns = [
        r"\bauid=\d+",
        r"\buid=\d+",
        r"\beuid=\d+",
        r"\bpid=\d+",
        r"\bcomm=",
        r"\bexe=",
    ]

    missing = [
        pattern for pattern in identity_patterns if not re.search(pattern, stdout)
    ]

    assert (
        not missing
    ), "stigcompliance: audit records missing identity fields: " + ", ".join(missing)
