"""
Ref: SRG-OS-000775-GPOS-00230

Verify the operating system is configured to include only approved trust
anchors in trust stores or certificate stores managed by the organization.
"""

import pytest


@pytest.mark.security_id(263659)
@pytest.mark.feature("sap")
def test_validate_fingerprint_of_SAP_CA_certificate(shell):
    """Verify the SAP Global Root CA certificate has the expected SHA-256 fingerprint."""
    cert_path = "/etc/ssl/certs/SAP_Global_Root_CA.pem"
    result = shell(
        f"openssl x509 -in {cert_path} -noout -fingerprint -sha256", capture_output=True
    )
    fingerprint = result.stdout.strip().split("=")[-1]

    assert (
        fingerprint
        == "56:53:9C:1E:7B:5E:D5:58:2B:79:68:00:61:CB:F2:14:86:A8:50:22:6B:2F:CF:30:B5:B1:52:A7:20:E1:34:DE"
    )
