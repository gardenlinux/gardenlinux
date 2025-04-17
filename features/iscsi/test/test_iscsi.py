import pytest
from helper.namespace import NamespaceSession
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def test_iscsi_setup(client, non_provisioner_chroot):
    with NamespaceSession(client, packages=["tgt"]) as n:
        n.run("start-stop-daemon --start --quiet --exec /usr/sbin/tgtd")

        n.run("dd if=/dev/zero of=/srv/iscsi_disk.img bs=1 count=0 seek=1G")

        iscsi_config = """<target iqn.2025-04.localhost:storage.disk1>
                backing-store /srv/iscsi_disk.img
                initiator-address 127.0.0.1
            </target>"""
        n.run(f"echo '{iscsi_config}' > /etc/tgt/conf.d/iscsi_target.conf")
        n.run("/usr/sbin/tgt-admin --update ALL")
        n.run("tgtadm --mode target --op show")
        n.run("iscsiadm -m discovery -t sendtargets -p 127.0.0.1")
        n.run("iscsiadm -m node --login")
