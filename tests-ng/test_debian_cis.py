import pytest
from plugins.debian_cis import DebianCIS

@pytest.mark.root(reason="Executing CIS/OVH /tmp/debian-cs tests requires superuser access")
@pytest.mark.booted(reason="cis hardening test execution needs root priv")
@pytest.mark.feature("cis")
@pytest.mark.modify(reason="feature/cis modifies the system to make it security compliant")
@pytest.mark.parametrize(
    "args",
    [
        {
            "git_debian_cis": "https://github.com/ovh/debian-cis.git",
            "git_debian_cis_branch": "master",
            "config_src": "/gardenlinux/features/cis/test/conf.d/",
            "config_dst": "/tmp/debian-cis/etc/conf.d/",
            "script_src": "/gardenlinux/features/cis/test/check_scripts/",
            "script_dst": "/tmp/debian-cis/bin/hardening/"
        }
    ]
)
def test_debian_cis(client, args, non_provisioner_chroot):
    DebianCIS(client, args)

