import pytest
from plugins.kernel_configs import KernelConfigs
from plugins.parse_file import ParseFile


@pytest.mark.feature("cloud or metal")
@pytest.mark.arch("amd64", reason="SGX is an amd64 option")
def test_kernel_configs_sgx(parse_file: ParseFile, kernel_configs: KernelConfigs):
    """Test that all kernel configs have SGX enabled for amd64."""
    for config in kernel_configs.get_installed():
        parsed_config = parse_file.parse(config.path, format="keyval")
        assert (
            parsed_config["CONFIG_X86_SGX"] == "y"
        ), f"CONFIG_X86_SGX not set to 'y' in {config.path}"
        assert (
            parsed_config["CONFIG_X86_SGX_KVM"] == "y"
        ), f"CONFIG_X86_SGX_KVM not set to 'y' in {config.path}"
