import re

import pytest
from plugins.parse_file import ParseFile
from plugins.shell import ShellRunner

APT_CONF_DIR = "/etc/apt/apt.conf.d"


@pytest.mark.feature("not container and not lima")
@pytest.mark.root(reason="required to verify package signature enforcement")
def test_package_signature_verification_enabled(
    parse_file: ParseFile, shell: ShellRunner
):
    """
    As per DISA STIG compliance requirement, the operating system must prevent the
    installation of patches, service packs, device drivers, or operating system components
    without verification they have been digitally signed using a certificate that is recognized
    and approved by the organization.
    Ref: SRG-OS-000366-GPOS-00153
    """

    result = shell(
        f"find {APT_CONF_DIR} -type f",
        capture_output=True,
        ignore_exit_code=True,
    )

    files = result.stdout.splitlines()

    insecure_pattern_1 = re.compile(r"AllowUnauthenticated\s*=\s*true", re.IGNORECASE)
    insecure_pattern_2 = re.compile(
        r"Acquire::AllowInsecureRepositories\s*=\s*true", re.IGNORECASE
    )

    for path in files:
        lines = parse_file.lines(path, ignore_missing=True)

        assert (
            insecure_pattern_1 not in lines
        ), f"stigcompliance: AllowUnauthenticated enabled in {path}"

        assert (
            insecure_pattern_2 not in lines
        ), f"stigcompliance: AllowInsecureRepositories enabled in {path}"
