import pytest

from plugins.apt import Apt
from plugins.deborphan import DebOrphan

@pytest.mark.root
@pytest.mark.feature("not booted")
def test_for_no_orphaned_files(apt: Apt, deborphan: DebOrphan):
    """
    Check for orphaned files from package installations.
    """
    assert apt.update() == True, f"updating package cache failed"
    assert apt.install("deborphan") == True, f"installing deborphan failed"
    assert deborphan.save_manually_installed_packages() == True, f"saving manually installed files failed"

    pkgs = deborphan.find_orphans()

    assert len(pkgs) == 0, f"Found {len(pkgs)} orphaned packages"