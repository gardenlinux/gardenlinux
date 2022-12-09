from helper import utils
import json
import logging
import tempfile
import shutil
import os
import pytest

# Define global logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def test_oci_feat(local, testconfig):
    """ This test does several steps using the results of a build with _oci feature:
    - verify neccessary testconfig options are present (image, kernel)
    - install the docker-registry into the container, provide a config, start the registry
    - extracts the testconfig["image"] file to retrieve the OCI fs layout
    - tag the extracted OCI image for uploading to the registry on localhost
    - push the OCI image to the local registry
    - retrieve the url for the kernel file out of the OCI image
    - download the kernel image
    - compare the downloaded kernel with the testconfig["kernel"]
    """

    # check for neccessary configuration options
    if not "image" in testconfig["oci"]:
        logger.error("No path to image archive defined.")
    else:
        image = testconfig["oci"]["image"]
        logger.info(f"Path to image archive defined: {image}")
    if not "kernel" in testconfig["oci"]:
        logger.error("No kernel to compare defined.")
    else:
        kernelcmp = testconfig["oci"]["kernel"]
        logger.info(f"Kernel to compare is defined: {kernelcmp}")

    # update package index files
    cmd = f"apt-get update"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Could not update Debian Package Index."
    logger.info(f"Updated Package Index.")

    # install docker-registry
    pkg = "docker-registry"
    cmd = f"apt-get install -y --no-install-recommends {pkg}"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Could not install Debian Package: {pkg}"
    logger.info(f"Installed {pkg}")

    # provide a config file for the registry
    # this will enable plain http serving without authentication
    docker_registry_config_src = "integration/misc/docker_registry_config_integrations_tests"
    docker_registry_config_dest = "/etc/docker/registry/config.yml"

    try:
        shutil.copy(docker_registry_config_src, docker_registry_config_dest)
        logger.info(f"Copied {docker_registry_config_src} to: {docker_registry_config_dest}")
    except OSError:
        logger.error(f"Could not copy {docker_registry_config_src} to: {docker_registry_config_dest}")

    cmd = f"/etc/init.d/docker-registry start"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Running {pkg} failed"
    logger.info(f"Running {pkg}")

    # extract the image
    ociextract = tempfile.mkdtemp(prefix="gl-int-oci-")
    logger.info(f"Created ociextract in {ociextract}")
    logger.info(f"Unarchiving image {image} to {ociextract}")
    cmd = f"tar xJvf {image} -C {ociextract}"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Unable to extract {image} to {ociextract}"

    # tag image and upload it
    with open(os.path.join(ociextract, "onmetal", "index.json")) as indexfile:
        onmetaldata = json.load(indexfile)
    assert "manifests" in onmetaldata
    assert len(onmetaldata["manifests"]) == 1
    assert "digest" in onmetaldata["manifests"][0]

    logger.info(f"Tagging image {image}")
    digest = onmetaldata["manifests"][0]["digest"]
    onmetalpath = os.path.join(ociextract, "onmetal")
    cmd = f"onmetal-image tag {digest} localhost:5000/gardenlinux:latest --store-path {onmetalpath}"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Unable to tag image using onmetal-image"
    logger.info(f"Successfully tagged image")

    # push the image to the local registy
    logger.info(f"Uploading image to local registry")
    cmd = f"onmetal-image push localhost:5000/gardenlinux:latest --store-path {onmetalpath}"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Unable to push image using onmetal-image to local registry"
    logger.info(f"Successfully uploaded image to local registry")

    # retrieve kernel layer
    logger.info(f"Retrieving url for kernel layer")
    cmd = f"onmetal-image --store-path {onmetalpath} url --layer kernel localhost:5000/gardenlinux:latest"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Kernel layer url: {out}"

    kernel = json.loads(out)
    assert "url" in kernel
    logging.info(f"URL for kernel layer: {kernel['url']}")

    # download the kernel using curl
    kernelfile = os.path.join(ociextract, "vmlinuz")
    logging.info(f"Downloading kernel to {kernelfile}")
    cmd = f"curl -o {kernelfile} {kernel['url']}"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"Could not download {kernel['url']} to {kernelfile}"

    # compare
    logging.info(f"Comparing {kernelfile} with {kernelcmp}")
    cmd = f"cmp {kernelfile} {kernelcmp}"
    rc, out = utils.execute_local_command(cmd)
    assert rc == 0, f"{kernelcmp} differs from {kernelfile}!"


