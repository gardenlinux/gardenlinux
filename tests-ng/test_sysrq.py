import pytest
from plugins.sysctl import Sysctl


@pytest.mark.booted("sysrq is only relevant in a booted environment")
def test_disable_sysrq(sysctl: Sysctl):
    """
    With the Magic SysRq key a user can debug the kernel and modify the system. This
    should not be possible in a production environment. Therefore kernel.sysrq should be
    disabled and not be found in the /proc/sys directory.

    See more: https://en.wikipedia.org/wiki/Magic_SysRq_key
    """
    with pytest.raises(KeyError):
        sysctl["kernel.sysrq"]


def test_persistent_disable_sysrq():
    """
    To ensure that the Magic Sysrq key is persistenly disabled, it should be turn off
    in the configuration file.

    See more: https://en.wikipedia.org/wiki/Magic_SysRq_key
    """
    with open("/etc/sysctl.d/10-disable-sysrq.conf", "r") as f:
        assert "kernel.sysrq = 0" in f.read(), f"kernel.sysrq is not disabled"
