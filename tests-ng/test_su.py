import pytest

@pytest.mark.root
def test_pam_wheel_is_required():
    """
    Validate that we have access to su restircted by default.  The test will
    read the file from `/etc/pam.d/su` and check if it has the configuration
    parameter we exepct.

    A user needs to be configured to be admitted to use `su`. By default, this
    is realized by a specify group, the `wheel` group. We have to ensure that
    this behavior is enabled.
    """    
    with open("/etc/pam.d/su", "r") as f:
        # ignore comments and blank lines
        entries = [line.strip() for line in f.readlines() if not line.strip().startswith("#") and len(line.strip()) > 0]

        assert any(
            "auth" in entry and "pam_wheel.so" in entry for entry in entries
        ), "Control value of PAM Module pam_wheel.so must be set to required"
