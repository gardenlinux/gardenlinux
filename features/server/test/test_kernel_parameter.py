from helper.tests.kernel_parameter import kernel_parameter
import pytest

@pytest.mark.parametrize(
    "parameter,value",
    [
        ("fs.protected_symlinks", 1),
        ("fs.protected_hardlinks", 1),
        ("kernel.randomize_va_space", 1)
    ]
)
def test_kernel_parameter(client, parameter, value):
    kernel_parameter(client, parameter, value)
