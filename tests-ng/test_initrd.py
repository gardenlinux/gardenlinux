import pytest
from plugins.initrd import Initrd
from plugins.parse_file import FileContent


@pytest.mark.feature("aws")
def test_aws_dracut_contains_xen_modules(file_content: FileContent):
    file = "/etc/dracut.conf.d/90-xen-blkfront-driver.conf"
    line = 'add_drivers+=" xen-blkfront "'
    found = file_content.check_line(file, line)
    assert found, f"Could not find line {line} in {file}."


@pytest.mark.feature("aws")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_aws_initrd_contains_xen_modules(initrd: Initrd):
    modules = ["xen-blkfront"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


@pytest.mark.feature("azure")
def test_azure_dracut_contains_nvme_modules(file_content: FileContent):
    file = "/etc/dracut.conf.d/67-azure-nvme-modules.conf"
    line = 'add_drivers+=" nvme nvme-core nvme-fabrics nvme-fc nvme-rdma nvme-loop nvmet nvmet-fc nvme-tcp "'
    found = file_content.check_line(file, line)
    assert found, f"Could not find line {line} in {file}."


@pytest.mark.feature("azure")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_azure_initrd_contains_nvme_modules(initrd: Initrd):
    modules = ["nvme-fabrics", "nvme-fc", "nvme-rdma"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"


@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_dracut_contains_broadcom_modules(file_content: FileContent):
    file = "/etc/dracut.conf.d/49-include-bnxt-drivers.conf"
    line = 'add_drivers+=" bnxt_en "'
    found = file_content.check_line(file, line)
    assert found, f"Could not find line {line} in {file}."


@pytest.mark.feature("openstackbaremetal")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_openstackbaremetal_initrd_contains_broadcom_modules(initrd: Initrd):
    modules = ["bnxt_en"]
    for module in modules:
        assert initrd.contains_module(module), f"{module} module not found in initrd"
