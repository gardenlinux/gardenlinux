import os
import shutil

import pytest
from handlers.pip import pip_requests
from plugins.dpkg import Dpkg
from plugins.shell import ShellRunner
from plugins.utils import tree


@pytest.mark.feature("pythonDev")
def test_python_environment_is_installed(shell: ShellRunner):
    dpkg = Dpkg(shell)

    assert dpkg.package_is_installed("python3"), "python3 package is not installed"
    assert dpkg.package_is_installed(
        "python3-pip"
    ), "python3-pip package is not installed"
    assert dpkg.package_is_installed(
        "python3.13-venv"
    ), "python3.13-venv package is not installed"


dependencies = {
    "arm64": {
        "/required_libs_test",
        "/required_libs_test/usr",
        "/required_libs_test/usr/lib",
        "/required_libs_test/usr/lib/aarch64-linux-gnu",
        "/required_libs_test/usr/lib/aarch64-linux-gnu/libpthread.so.0",
        "/required_libs_test/usr/lib/aarch64-linux-gnu/libc.so.6",
        "/required_libs_test/usr/lib/aarch64-linux-gnu/ld-linux-aarch64.so.1",
    },
    "amd64": {
        "/required_libs_test",
        "/required_libs_test/usr",
        "/required_libs_test/usr/lib",
        "/required_libs_test/usr/lib/x86_64-linux-gnu",
        "/required_libs_test/usr/lib/x86_64-linux-gnu/libpthread.so.0",
        "/required_libs_test/usr/lib/x86_64-linux-gnu/libc.so.6",
        "/required_libs_test/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2",
    },
}


@pytest.mark.feature("pythonDev")
@pytest.mark.root(reason="Installs pip packages")
@pytest.mark.modify(reason="Installs pip packages")
def test_python_export_libs(shell: ShellRunner, pip_requests):
    dpkg = Dpkg(shell)
    arch = dpkg.architecture_native()

    # Check if requests is installed
    shell("/bin/python3 -c 'import requests'")

    shell(
        f"exportLibs.py --package-dir {pip_requests} --output-dir /required_libs_test"
    )

    assert os.path.isdir("/required_libs_test"), "/required_libs_test was not created"

    assert (
        tree("/required_libs_test") == dependencies[arch]
    ), "required_libs content differs"

    shutil.rmtree("/required_libs_test")
