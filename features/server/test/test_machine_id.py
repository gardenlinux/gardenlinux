from helper.tests.machine_id import machine_id
from helper.tests.machine_id import machine_id_powered_on

def test_machine_id(client, chroot):
     machine_id(client)

def test_machine_id_powered_on(client, non_chroot):
     machine_id_powered_on(client)
