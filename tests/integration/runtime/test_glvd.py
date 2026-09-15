import pytest
from plugins.file import File

# =============================================================================
# glvd Feature
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-glvd-script-update-motd-glvd"])
@pytest.mark.feature("glvd")
def test_glvd_motd_scripts_exists(file: File):
    """Test that GLVD MOTD script exists"""
    paths = [
        "/etc/update-motd.d/99-glvd",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"
