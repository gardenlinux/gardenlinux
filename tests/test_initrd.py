import pytest
from plugins.initrd import Initrd
from plugins.parse_file import ParseFile


@pytest.mark.testcov(["GL-TESTCOV-aws-config-initrd-xen-blkfront"])
@pytest.mark.feature("aws")
def test_aws_dracut_contains_xen_modules(parse_file: ParseFile):
    file = "/etc/dracut.conf.d/90-xen-blkfront-driver.conf"
    line = 'add_drivers+=" xen-blkfront "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.testcov(["GL-TESTCOV-aws-config-initrd-xen-blkfront"])
@pytest.mark.feature("aws")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_aws_initrd_contains_xen_modules(initrd: Initrd):
    modules = ["xen-blkfront"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


@pytest.mark.testcov(["GL-TESTCOV-azure-config-initrd-nvme"])
@pytest.mark.feature("azure")
def test_azure_dracut_contains_nvme_modules(parse_file: ParseFile):
    file = "/etc/dracut.conf.d/67-azure-nvme-modules.conf"
    line = 'add_drivers+=" nvme nvme-core nvme-fabrics nvme-fc nvme-rdma nvme-loop nvmet nvmet-fc nvme-tcp "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.testcov(["GL-TESTCOV-azure-config-initrd-nvme"])
@pytest.mark.feature("azure")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_azure_initrd_contains_nvme_modules(initrd: Initrd):
    modules = ["nvme-fabrics", "nvme-fc", "nvme-rdma"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


@pytest.mark.testcov(["GL-TESTCOV-openstackMetal-config-initrd-bnxt"])
@pytest.mark.feature("openstack and metal")
def test_openstack_metal_dracut_contains_broadcom_modules(parse_file: ParseFile):
    file = "/etc/dracut.conf.d/49-include-bnxt-drivers.conf"
    line = 'add_drivers+=" bnxt_en "'
    lines = parse_file.lines(file)
    assert line in lines, f"Could not find line {line} in {file}."


@pytest.mark.testcov(["GL-TESTCOV-openstackMetal-config-initrd-bnxt"])
@pytest.mark.feature("openstack and metal")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_openstack_metal_initrd_contains_broadcom_modules(initrd: Initrd):
    modules = ["bnxt_en"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"
