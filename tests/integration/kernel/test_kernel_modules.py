import pytest
from plugins.file import File
from plugins.kernel_module import KernelModule

# =============================================================================
# cisModprobe Feature
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cisModprobe-config-modprobe-cramfs"
        "GL-SET-cisModprobe-config-modprobe-dccp"
        "GL-SET-cisModprobe-config-modprobe-freevxfs"
        "GL-SET-cisModprobe-config-modprobe-jffs2"
        "GL-SET-cisModprobe-config-modprobe-rds"
        "GL-SET-cisModprobe-config-modprobe-sctp"
        "GL-SET-cisModprobe-config-modprobe-squashfs"
        "GL-SET-cisModprobe-config-modprobe-tipc"
        "GL-SET-cisModprobe-config-modprobe-udf"
    ]
)
@pytest.mark.feature("cisModprobe")
def test_cismodprobe_blacklist_exists(file: File):
    """Test that kernel modules are blacklisted"""
    paths = [
        "/etc/modprobe.d/cramfs.conf",
        "/etc/modprobe.d/dccp.conf",
        "/etc/modprobe.d/freevxfs.conf",
        "/etc/modprobe.d/jffs2.conf",
        "/etc/modprobe.d/rds.conf",
        "/etc/modprobe.d/sctp.conf",
        "/etc/modprobe.d/squashfs.conf",
        "/etc/modprobe.d/tipc.conf",
        "/etc/modprobe.d/udf.conf",
    ]

    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-cisModprobe-config-modprobe-cramfs"
        "GL-SET-cisModprobe-config-modprobe-dccp"
        "GL-SET-cisModprobe-config-modprobe-freevxfs"
        "GL-SET-cisModprobe-config-modprobe-jffs2"
        "GL-SET-cisModprobe-config-modprobe-rds"
        "GL-SET-cisModprobe-config-modprobe-sctp"
        "GL-SET-cisModprobe-config-modprobe-squashfs"
        "GL-SET-cisModprobe-config-modprobe-tipc"
        "GL-SET-cisModprobe-config-modprobe-udf"
    ]
)
@pytest.mark.feature("cisModprobe")
def test_cismodprobe_modules_not_loaded(kernel_module: KernelModule):
    """Test that modules are not loaded"""
    modules = [
        "cramfs",
        "dccp",
        "freevxfs",
        "jffs2",
        "rds",
        "sctp",
        "squashfs",
        "tipc",
        "udf",
    ]

    for module in modules:
        assert not kernel_module.is_module_loaded(
            module
        ), f"Module {module} is loaded but should be deny listed"


# =============================================================================
# cloud Feature - Kernel Module Configurations
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-modprobe-firewire-disable",
        "GL-SET-cloud-config-modprobe-fs-disable",
        "GL-SET-cloud-config-modprobe-net-disable",
        "GL-SET-cloud-config-modprobe-usb-disable",
    ]
)
@pytest.mark.feature("cloud")
def test_cloud_modprobe_disable_configs_exist(file: File):
    """Test that cloud modprobe disable configurations exist"""
    paths = [
        "/etc/modprobe.d/disabled_firewire.conf",
        "/etc/modprobe.d/disabled_fs.conf",
        "/etc/modprobe.d/disabled_net.conf",
        "/etc/modprobe.d/disabled_usb.conf",
    ]
    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-modprobe-udf-disable",
    ]
)
@pytest.mark.feature(
    "cloud and not azure", reason="azure has a different modprobe disable configuration"
)
def test_cloud_modprobe_disable_udf_config_exists(file: File):
    """Test that cloud modprobe disable configurations exist, but not on Azure"""
    paths = [
        "/etc/modprobe.d/disabled_udf.conf",
    ]
    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-modprobe-firewire-disable",
        "GL-SET-cloud-config-modprobe-fs-disable",
        "GL-SET-cloud-config-modprobe-net-disable",
        "GL-SET-cloud-config-modprobe-usb-disable",
    ]
)
@pytest.mark.feature("cloud")
def test_cloud_modprobe_disable_modules_not_loaded(kernel_module: KernelModule):
    """Test that disabled modules are not loaded"""
    modules = [
        "firewire-core",
        "cramfs",
        "freevxfs",
        "jffs2",
        "hfs",
        "hfsplus",
        "dccp",
        "sctp",
        "rds",
        "tipc",
        "usbcore",
        "usb-common",
        "usb-storage",
    ]
    for module in modules:
        assert not kernel_module.is_module_loaded(
            module
        ), f"Module {module} is loaded but should be deny listed"


@pytest.mark.setting_ids(
    [
        "GL-SET-cloud-config-modprobe-udf-disable",
    ]
)
@pytest.mark.feature("cloud and not azure")
def test_cloud_modprobe_udf_module_not_loaded(kernel_module: KernelModule):
    """Test that disabled modules are not loaded, but not on Azure"""
    modules = [
        "udf",
    ]
    for module in modules:
        assert not kernel_module.is_module_loaded(
            module
        ), f"Module {module} is loaded but should be deny listed"


@pytest.mark.setting_ids(["GL-SET-azure-config-modprobe-no-udf-disable"])
@pytest.mark.feature("azure")
def test_azure_no_modprobe_udf_disable_exists(file: File):
    """Test that on Azure no modprobe disable configuration for UDF exists"""
    assert not file.exists("/etc/modprobe.d/disabled_udf.conf")


@pytest.mark.setting_ids(["GL-SET-azure-config-modprobe-no-udf-disable"])
@pytest.mark.root(reason="loading modules requires root access")
@pytest.mark.feature("azure")
def test_azure_modprobe_udf_module_loaded(kernel_module: KernelModule):
    """Test that UDF module is loaded on Azure"""
    modules = [
        "udf",
    ]
    for module in modules:
        kernel_module.load_module(module)
        assert kernel_module.is_module_loaded(
            module
        ), f"Module {module} is not loaded but should be loaded on Azure after loading"
    kernel_module.unload_modules()


# =============================================================================
# chost Feature - Kernel Module Configurations
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-modprobe-overlayfs",
        "GL-SET-chost-config-modules-load-br-netfilter",
        "GL-SET-chost-config-modules-load-ip-tables",
        "GL-SET-chost-config-modules-load-overlayfs",
    ]
)
@pytest.mark.feature("chost")
def test_chost_modprobe_configs_exist(file: File):
    """Test that chost modprobe configurations exist"""
    paths = [
        "/etc/modprobe.d/overlayfs.conf",
        "/etc/modules-load.d/br_netfilter.conf",
        "/etc/modules-load.d/ip_tables.conf",
        "/etc/modules-load.d/overlay.conf",
    ]
    missing = [path for path in paths if not file.exists(path)]
    assert not missing, f"The following files were not found: {', '.join(missing)}"


@pytest.mark.setting_ids(["GL-SET-chost-config-modprobe-overlayfs"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="module state check needs a booted system")
def test_chost_modprobe_overlayfs_loaded(kernel_module: KernelModule):
    """Test that overlay module is loaded with correct parameters"""

    module = "overlay"
    assert kernel_module.is_module_loaded(
        module
    ), f"Module {module} should be loaded for container host"

    module_parameters = [
        "metacopy=N",
        "redirect_dir=Y",
    ]
    missing = [
        module_parameter
        for module_parameter in module_parameters
        if not kernel_module.has_module_parameter(
            module, *module_parameter.split("=", 1)
        )
    ]
    assert (
        not missing
    ), f"Module {module} parameters are not set to the expected value: {', '.join(missing)}"


@pytest.mark.setting_ids(
    [
        "GL-SET-chost-config-modules-load-br-netfilter",
        "GL-SET-chost-config-modules-load-ip-tables",
    ]
)
@pytest.mark.feature("chost")
def test_chost_modprobe_required_modules_loaded(kernel_module: KernelModule):
    """Test that required modules are loaded on chost"""
    modules = [
        "br_netfilter",
        "ip_tables",
    ]
    missing = [
        module for module in modules if not kernel_module.is_module_loaded(module)
    ]
    assert (
        not missing
    ), f"The following modules are not loaded but should be loaded: {', '.join(missing)}"


# =============================================================================
# khost Feature - Kernel Module Configurations
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-khost-config-modules-load-br-nf"])
@pytest.mark.feature("khost")
def test_khost_modprobe_br_nf_exists(file: File):
    """Test that khost br-nf modprobe configuration exists"""
    assert file.is_regular_file("/etc/modules-load.d/br-nf.conf")


@pytest.mark.setting_ids(["GL-SET-khost-config-modules-load-br-nf"])
@pytest.mark.feature("khost")
def test_khost_modprobe_br_nf_loaded(kernel_module: KernelModule):
    """Test that khost br-nf module is loaded"""
    assert kernel_module.is_module_loaded(
        "br_netfilter"
    ), "br_netfilter module should be loaded for khost"


# =============================================================================
# gardener Feature - Kernel Module Configurations
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gardener-config-modules-load-ipvs"])
@pytest.mark.feature("gardener")
def test_gardener_modprobe_ipvs_exists(file: File):
    """Test that gardener ipvs modprobe configuration exists"""
    assert file.is_regular_file("/etc/modules-load.d/ipvs.conf")


@pytest.mark.setting_ids(["GL-SET-gardener-config-modules-load-ipvs"])
@pytest.mark.feature("gardener")
def test_gardener_modprobe_ipvs_loaded(kernel_module: KernelModule):
    """Test that gardener ipvs modules are loaded"""
    modules = [
        "ip_vs",
        "ip_vs_rr",
        "ip_vs_wrr",
        "ip_vs_sh",
        "nf_conntrack",
    ]
    missing = [
        module for module in modules if not kernel_module.is_module_loaded(module)
    ]
    assert (
        not missing
    ), f"The following modules are not loaded but should be loaded: {', '.join(missing)}"


# =============================================================================
# openstackbaremetal Feature - Kernel Module Configurations
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-config-modprobe-disallow-nouveau"])
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_modprobe_nouveau_disable_exists(file: File):
    """Test that OpenStack Baremetal nouveau disable configuration exists"""
    assert file.is_regular_file("/etc/modprobe.d/10-disallow-nouveau.conf")


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-config-modprobe-disallow-nouveau"])
@pytest.mark.feature("openstackbaremetal")
def test_openstackbaremetal_modprobe_nouveau_no_loaded(kernel_module: KernelModule):
    """Test that OpenStack Baremetal nouveau module is not loaded"""
    assert not kernel_module.is_module_loaded(
        "nouveau"
    ), "nouveau module should not be loaded for OpenStack Baremetal"
