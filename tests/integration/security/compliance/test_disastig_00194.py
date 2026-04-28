"""
Ref: SRG-OS-000437-GPOS-00194

Verify the operating system removes all software components after updated
versions have been installed.
"""


def test_no_residual_software_components(shell):
    """
    If a package is in 'rc' state, it means the package was
    removed but configuration files (components) remain.
    """
    package_statuses = shell(
        "dpkg-query -W -f='${Status} ${Package}\n'", capture_output=True
    )

    residual_packages = [
        pkg.split()[-1]
        for pkg in package_statuses.stdout.splitlines()
        if "deinstall ok config-files" in pkg
    ]

    assert not residual_packages, (
        f"Software components (config files) "
        f"were not removed after package updates/removal: {residual_packages}"
    )
