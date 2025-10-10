from pathlib import Path
import pytest

from plugins.shell import ShellRunner

expected_capabilities_by_feature = {
    "kvm": ["/usr/bin/arping cap_net_raw=ep"],
    "vmware": ["/usr/bin/arping cap_net_raw=ep"],
}

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
