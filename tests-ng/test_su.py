import pytest

from plugins.pam import PamConfig


@pytest.mark.security_id(166)
@pytest.mark.root
@pytest.mark.feature("not container")
@pytest.mark.parametrize("pam_config", [("/etc/pam.d/su")], indirect=["pam_config"])
def test_pam_wheel_is_required(pam_config: PamConfig):
    """
    Validate that we have access to su restircted by default.  The test will
    read the file from `/etc/pam.d/su` and check if it has the configuration
    parameter we exepct.

    A user needs to be configured to be admitted to use `su`. By default, this
    is realized by a specify group, the `wheel` group. We have to ensure that
    this behavior is enabled.

    This line should be defined:

        auth       required pam_wheel.so

    """
    pam_config.find_entries()

    candidates = pam_config.find_entries(
        type_="auth", control_contains="required", module_contains="pam_wheel.so"
    )

    assert (
        len(candidates) == 1
    ), "Control value of PAM Module pam_wheel.so must be set to required"
