import pytest
from plugins.kernel_configs import KernelConfigs
from plugins.parse_file import FileContent


@pytest.mark.feature("cloud or metal")
@pytest.mark.arch("amd64", reason="SGX is an amd64 option")
def test_kernel_configs_sgx(file_content: FileContent, kernel_configs: KernelConfigs):
    """Test that all kernel configs have SGX enabled for amd64."""
    for config in kernel_configs.get_installed():
        mapping = {
            "CONFIG_X86_SGX": "y",
            "CONFIG_X86_SGX_KVM": "y",
        }
        format = "keyval"
        result = file_content.get_mapping(
            config.path,
            mapping,
            format=format,
        )
        assert result is not None, f"Could not parse file: {config.path}"
        assert result.all_match, (
            f"Could not find expected mapping in {config.path} (format={format}) for {mapping}. "
            f"missing={result.missing}, wrong={{{', '.join(f'{k}:{v[1]!r}!={v[0]!r}' for k, v in result.wrong.items())}}}"
        )
