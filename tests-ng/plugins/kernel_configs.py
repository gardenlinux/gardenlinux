import glob
import platform

import pytest


@pytest.fixture(scope="session")
def kernel_config_paths():
    """Get all available /boot/config-* files."""
    configs = sorted(glob.glob("/boot/config-*"))
    assert configs, "No kernel config files found under /boot/config-*"
    return configs


@pytest.fixture(scope="session")
def system_architecture():
    """Normalized architecture string, e.g. 'amd64'."""
    arch = platform.machine()
    # Normalize to Debian-style arch labels
    if arch == "x86_64":
        arch = "amd64"
    elif arch.startswith("arm"):
        arch = "arm64"
    return arch


@pytest.fixture(scope="session")
def kernel_config_dict(kernel_config_paths):
    """
    Parse kernel config files into a dictionary of dictionaries:
    {
        '/boot/config-6.1.0-21-amd64': {
            'CONFIG_X86_SGX': 'y',
            'CONFIG_MAGIC_SYSRQ': 'n',
            ...
        },
        ...
    }
    """
    all_configs = {}

    for path in kernel_config_paths:
        config = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or not line.startswith("CONFIG_"):
                    continue
                key, _, value = line.partition("=")
                value = value.strip('"')  # strip quotes
                config[key] = value
        all_configs[path] = config

    return all_configs
