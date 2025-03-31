import pytest
from helper.utils import execute_remote_command
from helper.utils import get_package_list


def test_node_conformance(client, non_provisioner_chroot):
	# Make sure kubelet is installed. 
    assert "kubelet" in get_package_list(client), "kubelet is not installed"
	# Make sure podman or docker runtime is available 
    assert "podman" in get_package_list(client) or "docker" in get_package_list(client), "podman or docker is not installed"
	# Start node conformance tests 
    # Execute the node conformance testsLOG_DIR is the test output path.
    # sudo docker run -it --rm --privileged --net=host \
    #  -v /:/rootfs -v $CONFIG_DIR:$CONFIG_DIR -v $LOG_DIR:/var/result \
    #  registry.k8s.io/node-test:0.2

    config_dir = "/etc/kubernetes"
    log_dir = "/tmp"
    container_image = "registry.k8s.io/node-test:0.2"
    command = f"sudo docker run -it --rm --privileged --net=host -v /:/rootfs -v {config_dir}:{config_dir} -v {log_dir}:/var/result {container_image}"

    output = execute_remote_command(client, command)

	# Check results
