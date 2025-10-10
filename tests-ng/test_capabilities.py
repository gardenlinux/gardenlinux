from pathlib import Path
import pytest

from plugins.shell import ShellRunner

expected_capabilities_by_feature = {
    "kvm": ["/usr/bin/arping cap_net_raw=ep"],
    "vhost": ["/usr/lib/(aarch64|x86_64)-linux-gnu/gstreamer1.0/gstreamer-1.0/gst-ptp-helper cap_net_bind_service,cap_net_admin=ep"],
    "vmware": ["/usr/bin/arping cap_net_raw=ep"],
}

@pytest.mark.root
def test_only_expected_capabilities_are_defined(shell: ShellRunner, active_features):
    expected_capabilities = []
    for feature in active_features:
        expected_capabilities.extend(expected_capabilities_by_feature.get(feature, []))

    actual_capabilities = []
    paths = ["/boot", "/etc", "/usr", "/var"]
    for base in paths:
        for path in Path(base).rglob("*"):
            if path.is_file():
                try:
                    output = shell(f"/usr/sbin/getcap {str(path)}", capture_output=True).stdout.strip()
                    if output:
                        actual_capabilities.extend(output.splitlines())
                except:
                    continue

    assert set(actual_capabilities) == set(expected_capabilities), f"Expected this list of capabilities {expected_capabilities} but got {actual_capabilities}"
