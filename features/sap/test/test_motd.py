import pytest
from helper.utils import read_file_remote

@pytest.mark.security_id(480)
def test_for_motd(client, non_container):
    issue = read_file_remote(client, "/etc/issue")
    issue_net = read_file_remote(client, "/etc/issue.net")
    legal = """ATTENTION – UNAUTHORIZED ACCESS IS PROHIBITED
You are accessing SAP computer systems and network through which you may have access to business sensitive information (“SAP Systems”). SAP Systems are intended for legitimate business use by authorized users of SAP only. Personal use of the SAP Systems you are about to access is not permitted.

Unless applicable law provides otherwise, (i) any information stored in, transmitted through or processed by SAP Systems remains at all times the property of SAP, (ii) SAP has the right to scan and monitor access to and use of SAP Systems, and (iii) any information on SAP Systems and any processing activities relating to such information can be inspected by SAP at any time.

Except as may be provided by applicable law, you should have no expectation of privacy as to any information stored in, transmitted through or processed by any portion of SAP Systems. Unauthorized access or use of SAP Systems may result in disciplinary and legal action."""
    assert legal.split('\n') == issue, "SAP legal text is missing"
    assert legal.split('\n') == issue_net, "SAP legal text is missing"
