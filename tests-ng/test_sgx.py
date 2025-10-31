import pytest
from plugins.kernel_configs import KernelConfigs
from plugins.parse_file import FileContent


@pytest.mark.feature("cloud or metal")
@pytest.mark.arch("amd64", reason="SGX is an amd64 option")
def test_kernel_configs_sgx(file_content: FileContent, kernel_configs: KernelConfigs):
    """Test that all kernel configs have SGX enabled for amd64."""
    for config in kernel_configs.get_installed():
        file_content.assert_mapping(
            config.path,
            {
                "CONFIG_X86_SGX": "y",
                "CONFIG_X86_SGX_KVM": "y",
            },
            format="keyval",
        )
