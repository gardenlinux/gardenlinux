import pytest
from plugins.kernel_configs import KernelConfigs
from plugins.parse_file import ParseFile


@pytest.mark.feature("cloud or metal")
@pytest.mark.arch("amd64", reason="SGX is an amd64 option")
def test_kernel_configs_sgx(parse_file: ParseFile, kernel_configs: KernelConfigs):
    """Test that all kernel configs have SGX enabled for amd64."""
    for config in kernel_configs.get_installed():
        expected = {
            "CONFIG_X86_SGX": "y",
            "CONFIG_X86_SGX_KVM": "y",
        }
        format = "keyval"
        result = parse_file.match_values(config.path, expected, format=format)
        assert result.all_match, (
            f"Could not find expected mapping in {config.path} (format={format}) for {expected}. "
            f"missing={result.missing}, wrong={result.wrong_list}"
        )
