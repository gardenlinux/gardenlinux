import pytest
from plugins.file import File
from plugins.parse_file import ParseFile

# =============================================================================
# clamav Feature
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-clamav-config-cron-root",
    ]
)
@pytest.mark.feature("clamav")
def test_clamav_cron_exists(file: File):
    """Test that clamav cron job exists"""
    cron_locations = [
        "/var/spool/cron/crontabs/root",
    ]
    exists = any(file.exists(loc) for loc in cron_locations)
    assert (
        exists
    ), f"Clamav cron job should exist in one of: {', '.join(cron_locations)}"


@pytest.mark.testcov(
    [
        "GL-TESTCOV-clamav-config-cron-root",
    ]
)
@pytest.mark.feature("clamav")
def test_clamav_cron_content(parse_file: ParseFile):
    """Test that clamav cron job contains the correct content"""
    lines = parse_file.lines("/var/spool/cron/crontabs/root")
    assert lines == [
        "0 30 * * * root /usr/bin/clamscan -ri / >> /var/log/clamav/clamd.log",
    ], "Clamav cron job should contain the correct content"
