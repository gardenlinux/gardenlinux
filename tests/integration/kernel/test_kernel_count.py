import pytest
from plugins.kernel_versions import KernelVersions


@pytest.mark.feature("not container", reason="kernel is not installed in container")
def test_kernel_versions(kernel_versions: KernelVersions):
    """Test that only one kernel is installed."""
    installed_kernel_versions = kernel_versions.get_installed()
    assert (
        len(installed_kernel_versions) == 1
    ), f"Only one kernel should be installed, but {len(installed_kernel_versions)} were found"


@pytest.mark.feature("container", reason="kernel is not installed in container")
def test_kernel_versions_container(kernel_versions: KernelVersions):
    """Test that no kernel is installed in container."""
    installed_kernel_versions = kernel_versions.get_installed()
    assert (
        len(installed_kernel_versions) == 0
    ), f"No kernel should be installed, but {len(installed_kernel_versions)} were found"
