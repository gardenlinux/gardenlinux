import pytest
from plugins.parse_file import ParseFile


@pytest.mark.feature("disaSTIGmedium")
@pytest.mark.root(reason="requires access to /etc/login.defs")
def test_default_umask_is_077(parse_file: ParseFile):
    """
    As per DISA STIG compliance requirements, the operating system must set the
    default umask for all local interactive user accounts to 077 to prevent
    unauthorized access to newly created files.
    Ref: SRG-OS-000480-GPOS-00228
    """
    config = parse_file.parse("/etc/login.defs", format="spacedelim")

    assert config.get("UMASK") == "077", (
        f"stigcompliance: UMASK is not set to 077 in /etc/login.defs "
        f"(value={config.get('UMASK')!r})"
    )
