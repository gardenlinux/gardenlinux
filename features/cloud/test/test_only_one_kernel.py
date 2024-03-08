import pytest
import helper.utils as utils

def test_number_installed_kernels(client):
    """ Only one kernel should be installed """
    installed_kernels = utils.get_installed_kernel_versions(client)
    number_of_kernels = len(installed_kernels)
    assert number_of_kernels == 1, f"Number of installed kernels {nr_kernels} != 1"

