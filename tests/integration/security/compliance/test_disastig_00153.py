import re

import pytest
from plugins.find import Find
from plugins.parse_file import ParseFile

APT_CONF_DIR = "/etc/apt/apt.conf.d"


@pytest.mark.feature("not container and not lima and not baremetal")
@pytest.mark.root(reason="required to verify package signature enforcement")
def test_package_signature_verification_enabled(parse_file: ParseFile, find: Find):
    """
    As per DISA STIG compliance requirement, the operating system must prevent the
    installation of patches, service packs, device drivers, or operating system components
    without verification they have been digitally signed using a certificate that is recognized
    and approved by the organization.
    Ref: SRG-OS-000366-GPOS-00153
    """

    find.root_paths = APT_CONF_DIR
    find.entry_type = "files"

    insecure_pattern_1 = re.compile(r"AllowUnauthenticated\s*=\s*true", re.IGNORECASE)
    insecure_pattern_2 = re.compile(
        r"Acquire::AllowInsecureRepositories\s*=\s*true", re.IGNORECASE
    )

    for path in find:
        lines = parse_file.lines(path, ignore_missing=True)

        assert (
            insecure_pattern_1 not in lines
        ), f"stigcompliance: AllowUnauthenticated enabled in {path}"

        assert (
            insecure_pattern_2 not in lines
        ), f"stigcompliance: AllowInsecureRepositories enabled in {path}"
