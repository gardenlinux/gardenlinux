def install_test_dependencies(client, packages_list):
    """
    Installs a list of packages for testing.
    """
    for package in packages_list:
        install_test_package(client, package)


def install_test_package(client, package_name):
    """
    Installs a test package for testing.
    """
    (exit_code, output, error) = client.execute_command(
        f"DEBIAN_FRONTEND=noninteractive apt-get install -y {package_name}", quiet=True
    )
    assert exit_code == 0, f"Failed to install {package_name}: {error}"


def uninstall_test_dependencies(client, packages_list):
    """
    Uninstalls a list of packages after testing.
    """
    for package in packages_list:
        uninstall_test_package(client, package)


def uninstall_test_package(client, package_name):
    """
    Purges a previously installed test package.
    """
    (exit_code, output, error) = client.execute_command(
        f"DEBIAN_FRONTEND=noninteractive apt-get purge -y {package_name}", quiet=True
    )
    assert exit_code == 0, f"Failed to purge {package_name}: {error}"


def create_overlay_fs(client):
    # Create necessary directories and mount overlay fs
    commands = [
        "sudo mkdir -p /run/node/usr",
        "sudo mount /dev/disk/by-label/USR /run/node/usr",
        "sudo mkdir -p /run/node/ovl/u",
        "sudo mkdir -p /run/node/ovl/w",
        "sudo mount -t overlay overlay -o lowerdir=/run/node/usr,upperdir=/run/node/ovl/u,workdir=/run/node/ovl/w /usr",
    ]

    for command in commands:
        (exit_code, _, error) = client.execute_command(command, quiet=True)
        assert exit_code == 0, f"Failed to execute command: {command}\nError: {error}"


def cleanup_overlay_fs(client):
    commands = [
        "sudo umount /run/node/usr",
        "sudo rm -rf /run/node/ovl/w",
        "sudo rm -rf /run/node/ovl/u",
    ]

    for command in commands:
        (exit_code, _, error) = client.execute_command(command, quiet=True)
        assert exit_code == 0, f"Failed to execute command: {command}\nError: {error}"
