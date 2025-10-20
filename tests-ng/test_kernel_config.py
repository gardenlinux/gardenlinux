import pytest


@pytest.mark.parametrize(
    "key,expected,rationale,arch",
    [
        ("CONFIG_X86_SGX", "y", "Enable SGX", "amd64"),
        ("CONFIG_X86_SGX_KVM", "y", "Enable SGX for KVM guests", "amd64"),
        ("CONFIG_MAGIC_SYSRQ", "n", "Security risk if enabled", "all"),
    ],
)
def test_kernel_config_values(
    key, expected, rationale, arch, kernel_config_dict, system_architecture
):
    """Ensure key kernel config options have expected values."""

    # Arrange
    relevant_configs = [
        (path, config)
        for path, config in kernel_config_dict.items()
        if arch == "all" or arch in path or arch == system_architecture
    ]
    if not relevant_configs:
        pytest.skip(f"No kernel configs found for arch {arch}")

    # Act / Assert
    for path, config in relevant_configs:
        value = config.get(key, None)

        if expected == "n":
            assert value in (None, "n"), (
                f"{key} should be disabled ({rationale}) "
                f"but is set to '{value}' in {path}"
            )
        else:
            assert value == expected, (
                f"{key} should be '{expected}' ({rationale}) "
                f"but is '{value}' in {path}"
            )
