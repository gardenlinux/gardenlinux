from helper.utils import execute_remote_command as run
from helper.utils import read_file_remote
import pytest


@pytest.mark.security_id(171)
def test_for_nis(client, non_container):
    """
    Check if we have no NIS related entries.
    A passwd will then have an entry like this:
    +::::::

    Also the /etc/nsswitch will have entries as well.
    """

    for nssl_file in ["passwd", "shadow", "group", "gshadow"]:
        #  Name Service Switch libraries
        nssl = run(client, cmd=f"getent {nssl_file}")
        # Assume that when no + is prsent that the split will never return more
        # than one element.
        assert 1 == len(nssl.split("+")), f"NIS entry detected in {nssl_file}!"

    nsswitch = read_file_remote(client,
                                file="/etc/nsswitch.conf",
                                remove_comments=True)

    # Filtering fileds for nis, nisplus, compat
    nis_entries = list(filter(lambda x: 'nis' in x, nsswitch))
    nisplus_entries = list(filter(lambda x: 'nisplus' in x, nsswitch))
    compact_entries = list(filter(lambda x: 'compat' in x, nsswitch))

    assert 0 == len(nis_entries), "We found a nis entry in /etc/nsswitch.conf!"
    assert 0 == len(nisplus_entries), "We found nisplus in /etc/nsswitch.conf!"
    assert 0 == len(compact_entries), "We found compat  in /etc/nsswitch.conf!"
