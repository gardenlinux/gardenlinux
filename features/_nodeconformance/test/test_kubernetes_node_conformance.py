import pytest
import re
from helper.utils import execute_remote_command
from helper.utils import get_package_list
import logging


PACKAGES_GARDEN_LINUX = "docker-cli docker.io"
PACKAGES_KUBERNETES = "kubelet kubectl"
K8S_PGP_APT_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.5 (GNU/Linux)

mQENBGMHoXcBCADukGOEQyleViOgtkMVa7hKifP6POCTh+98xNW4TfHK/nBJN2sm
u4XaiUmtB9UuGt9jl8VxQg4hOMRf40coIwHsNwtSrc2R9v5Kgpvcv537QVIigVHH
WMNvXeoZkkoDIUljvbCEDWaEhS9R5OMYKd4AaJ+f1c8OELhEcV2dAQLLyjtnEaF/
qmREN+3Y9+5VcRZvQHeyBxCG+hdUGE740ixgnY2gSqZ/J4YeQntQ6pMUEhT6pbaE
10q2HUierj/im0V+ZUdCh46Lk/Rdfa5ZKlqYOiA2iN1coDPIdyqKavcdfPqSraKF
Lan2KLcZcgTxP+0+HfzKefvGEnZa11civbe9ABEBAAG0PmlzdjprdWJlcm5ldGVz
IE9CUyBQcm9qZWN0IDxpc3Y6a3ViZXJuZXRlc0BidWlsZC5vcGVuc3VzZS5vcmc+
iQE+BBMBCAAoBQJnFF34AhsDBQkIK2yBBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIX
gAAKCRAjRlTamilkNtOACACDK9dQ8CH2Ji9C3Q926nVMUiXdyJK1onCBrQSEBqdR
LJaT6hGx5pzxkQGgUDpS9p7LA0u920HKLwGb7yIAWtyE5TAj2CYprGgpq98sfsGC
+U5T9IrAdya/BaTAkkP6gNhfMjNaK3bOWsvuLRlluKMNch4ify+IwLqc1JLG40bj
2HnKBGYkC3m0VtQfUuPQMImSLta/NwRHJMPo8jfGyManqMMxp35/ecP2rXMfb/l1
WjFDY7h+6nqXay20ljMXkN23W8wFTdvC6lq45wwM5IBnKNR/TjNNYAIizZoHFWz1
c/ecMWWWCB2S7WbY4xI3JSCOD4XIff3ie7pc68/kgPytiQIcBBMBAgAGBQJjB6F3
AAoJEM8Lkoze1k873TQP/0t2F/jltLRQMG7VCLw7+ps5JCW5FIqu/S2i9gSdNA0E
42u+LyxjG3YxmVoVRMsxeu4kErxr8bLcA4p71W/nKeqwF9VLuXKirsBC7z2syFiL
Ndl0ARnC3ENwuMVlSCwJO0MM5NiJuLOqOGYyD1XzSfnCzkXN0JGA/bfPRS5mPfoW
0OHIRZFhqE7ED6wyWpHIKT8rXkESFwszUwW/D7o1HagX7+duLt8WkrohGbxTJ215
YanOKSqyKd+6YGzDNUoGuMNPZJ5wTrThOkTzEFZ4HjmQ16w5xmcUISnCZd4nhsbS
qN/UyV9Vu3lnkautS15E4CcjP1RRzSkT0jka62vPtAzw+PiGryM1F7svuRaEnJD5
GXzj9RCUaR6vtFVvqqo4fvbA99k4XXj+dFAXW0TRZ/g2QMePW9cdWielcr+vHF4Z
2EnsAmdvF7r5e2JCOU3N8OUodebU6ws4VgRVG9gptQgfMR0vciBbNDG2Xuk1WDk1
qtscbfm5FVL36o7dkjA0x+TYCtqZIr4x3mmfAYFUqzxpfyXbSHqUJR2CoWxlyz72
XnJ7UEo/0UbgzGzscxLPDyJHMM5Dn/Ni9FVTVKlALHnFOYYSTluoYACF1DMt7NJ3
oyA0MELL0JQzEinixqxpZ1taOmVR/8pQVrqstqwqsp3RABaeZ80JbigUC29zJUVf
=Eplj
-----END PGP PUBLIC KEY BLOCK-----"""


def create_overlay_fs(client, logger):
    logger.info("Creating overlay fs")
    execute_remote_command(
        client, "sudo mkdir -p /overlay/usr_work /overlay/usr_merged /overlay/usr_upper"
    )

    execute_remote_command(
        "mount -t overlay overlay -o lowerdir=/usr,upperdir=/overlay/usr_upper,workdir=/overlay/usr_merged /overlay/user_merged"
    )
    logger.info("after mount overlay fs")


def cleanup_overlay_fs(client, logger):
    logger.info("Cleaning up overlay fs")
    execute_remote_command(client, "sudo umount /overlay/usr_merged")
    execute_remote_command(
        client,
        "sudo rm -rf /overlay/usr_work /overlay/usr_merged /overlay/usr_upper",
    )


def setup_node_conformance(client, logger):
    logger.info("Setting up node conformance test")
    create_overlay_fs(client, logger)
    install_test_dependencies(client, logger)
    install_kubernetes_tools(client, logger)


def cleanup_node_conformance(client, logger):
    logger.info("Cleaning up node conformance test")

    # remove the K8s PGP key
    execute_remote_command(
        client, "sudo rm -f /etc/apt/keyrings/kubernetes-apt-keyring.gpg"
    )

    # remove installed packages
    execute_remote_command(client, f"sudo apt-get remove -y {PACKAGES_KUBERNETES}")
    execute_remote_command(client, f"sudo apt-get remove -y {PACKAGES_GARDEN_LINUX}")
    cleanup_overlay_fs(client, logger)


def install_test_dependencies(client, logger):
    logger.info("Installing test dependencies")

    execute_remote_command(client, "apt-get update")
    logger.info("after apt-get update")

    execute_remote_command(
        client,
        f"export DEBIAN_FRONTEND=noninteractive TERM=xterm; apt-get install -y {PACKAGES_GARDEN_LINUX}",
    )
    logger.info("after install_test_dependencies")


def install_kubernetes_tools(client, logger):
    logger.info("Installing Kubernetes tools")

    # store key K8s PGP key in a temp directory
    execute_remote_command(client, f"echo '{K8S_PGP_APT_KEY}' > /tmp/k8s-pgp-key")

    execute_remote_command(
        client,
        f"sudo gpg --batch --no-tty --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg /tmp/k8s-pgp-key",
    )

    logger.info("after gpg key import")
    add_sources_list_command = f"echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.32/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list"
    execute_remote_command(client, add_sources_list_command)
    logger.info("after add_sources_list_command")
    command = f"export DEBIAN_FRONTEND=noninteractive; sudo apt-get update && sudo apt-get install --no-install-recommends -y {PACKAGES_KUBERNETES}"
    output = execute_remote_command(client, command)
    logger.info("after install_kubernetes_tools")
    assert "kubelet" in get_package_list(client), "kubelet is not installed"
    assert "kubectl" in get_package_list(client), "kubectl is not installed"


def test_node_conformance(client, non_provisioner_chroot):
    try:
        logging.basicConfig(level=logging.INFO)  # Set logging level
        logger = logging.getLogger(__name__)
        logger.info("Running node conformance test")
        # get list of packages installed before running the test
        before_packages = get_package_list(client)

        setup_node_conformance(client, logger)

        # Make sure kubelet is installed.
        assert "kubelet" in get_package_list(client), "kubelet is not installed"
        # Make sure podman or docker runtime is available
        assert "docker" in get_package_list(client) or "docker" in get_package_list(
            client
        ), "podman or docker is not installed"
        # Start node conformance tests
        # Execute the node conformance testsLOG_DIR is the test output path.
        # sudo docker run -it --rm --privileged --net=host \
        #  -v /:/rootfs -v $CONFIG_DIR:$CONFIG_DIR -v $LOG_DIR:/var/result \
        #  registry.k8s.io/node-test:0.2

        logger.info("before node confortmance test")
        config_dir = "/etc/kubernetes"
        log_dir = "/tmp"
        container_image = "registry.k8s.io/node-test:0.2"
        command = f"sudo docker run --rm --privileged --net=host -v /:/rootfs -v {config_dir}:{config_dir} -v {log_dir}:/var/result {container_image}"

        code, output = execute_remote_command(client, command, skip_error=True)

        # present output without ansi
        print(re.sub(r"\x1b\[[0-9;]*m", "", output))
        # show logdir
        execute_remote_command(client, f"ls -l {log_dir}")
        assert False, "Node conformance test failed. Check the logs in /tmp"

        logger.info(f"{output}")
        logger.info("after node conformance test")

        remount_usr_readonly(client, logger)

        # get list of packages installed after running the test
        after_packages = get_package_list(client)
        assert (
            after_packages == before_packages
        ), "Test has side effects on the system. Packages installed after running the test: {}".format(
            set(after_packages) - set(before_packages)
        )

        # get container images installed after running the test
        after_images = execute_remote_command(client, "docker images")
        assert (
            after_images == before_images
        ), "Test has side effects on the system. Images installed after running the test: {}".format(
            set(after_images) - set(before_images)
        )
    finally:
        logger.info("Cleaning up node conformance test")
        cleanup_node_conformance(client, logger)


# Check results
