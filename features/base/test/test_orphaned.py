from helper.tests.orphaned import orphaned

# Execute the orphaned check only on chroot
# since it must install some packages that
# may not be possible on running machines.
def test_orphaned(client, provisioner_chroot, non_container):
    orphaned(client)
