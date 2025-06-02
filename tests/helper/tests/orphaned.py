from helper.utils import AptUpdate
from helper.utils import execute_remote_command
from helper.utils import install_package_deb


def orphaned(client):
    """ Test for orphaned files """
    # Update repo info and install package(s)
    AptUpdate(client)
    install_package_deb(client, "deborphan")

    # Add manual installed packages to keep
    cmd = "DEBIAN_FRONTEND=noninteractive apt-mark showmanual > /var/lib/deborphan/keep"
    out = execute_remote_command(client, cmd, sudo=True)

    # Run deborphan on remote platform
    cmd = "deborphan -an --no-show-section"
    out = execute_remote_command(client, cmd)

    # Get orphaned packages
    pkgs_found = []
    for pkg in out.split('\n'):
        if pkg != '':
            pkgs_found.append(pkg)

    assert not pkgs_found, f"Found orphaned packages: {pkgs_found}"
