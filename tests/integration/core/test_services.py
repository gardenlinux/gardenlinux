"""
Test systemd services for enabled/disabled, active/inactive states across all Garden Linux features.
"""

import pytest
from plugins.file import File
from plugins.kernel_versions import KernelVersions
from plugins.systemd import Systemd

# =============================================================================
# _fwcfg Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-_fwcfg-service-qemu-fw_cfg-script-unit"])
@pytest.mark.feature("_fwcfg")
def test_fwcfg_qemu_fw_cfg_script_unit_exists(file):
    """Test that qemu-fw_cfg-script.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/qemu-fw_cfg-script.service")


@pytest.mark.testcov(["GL-TESTCOV-_fwcfg-service-qemu-fw_cfg-script-enable"])
@pytest.mark.feature("_fwcfg")
@pytest.mark.booted(reason="Requires systemd")
def test__fwcfg_qemu_fw_cfg_script_service_enabled(systemd: Systemd):
    """Test that qemu-fw_cfg-script.service is enabled"""
    assert systemd.is_enabled("qemu-fw_cfg-script.service")


@pytest.mark.testcov(["GL-TESTCOV-_fwcfg-service-qemu-fw_cfg-script-enable"])
@pytest.mark.feature("_fwcfg and not disaSTIGmedium")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor("qemu", reason="qemu-fw_cfg-script only works on Qemu")
def test__fwcfg_qemu_fw_cfg_script_service_active(systemd: Systemd):
    """Test that qemu-fw_cfg-script.service is active"""
    assert systemd.is_active("qemu-fw_cfg-script.service")


# =============================================================================
# _kdump Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-_kdump-service-kdump-tools-enable"])
@pytest.mark.feature("_kdump")
@pytest.mark.booted(reason="Requires systemd")
def test__kdump_kdump_tools_service_enabled(systemd: Systemd):
    """Test that kdump-tools.service is enabled"""
    assert systemd.is_enabled("kdump-tools.service")


@pytest.mark.testcov(["GL-TESTCOV-_kdump-service-kdump-tools-enable"])
@pytest.mark.feature("_kdump")
@pytest.mark.booted(reason="Requires systemd")
def test__kdump_kdump_tools_service_active(systemd: Systemd):
    """Test that kdump-tools.service is active"""
    assert systemd.is_active("kdump-tools.service")


# =============================================================================
# _prod Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-_prod-service-no-systemd-coredump"])
@pytest.mark.feature("_prod")
@pytest.mark.booted(reason="Requires systemd")
def test__prod_no_systemd_coredump_service(systemd: Systemd):
    """Test that systemd-coredump.service is not installed"""
    assert not any(
        u.unit == "systemd-coredump.service" for u in systemd.list_installed_units()
    )


# =============================================================================
# aws Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-aws-service-aws-clocksource-unit"])
@pytest.mark.feature("aws")
def test_aws_clocksource_unit_exists(file):
    """Test that aws-clocksource.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/aws-clocksource.service")


@pytest.mark.testcov(["GL-TESTCOV-aws-service-aws-clocksource-enable"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_aws_clocksource_service_enabled(systemd: Systemd):
    """Test that aws-clocksource.service is enabled"""
    assert systemd.is_enabled("aws-clocksource.service")


@pytest.mark.testcov(["GL-TESTCOV-aws-service-aws-clocksource-enable"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_aws_clocksource_service_inactive(systemd: Systemd):
    """Test that aws-clocksource.service is inactive (oneshot service)"""
    assert systemd.is_inactive("aws-clocksource.service")


# =============================================================================
# checkbox Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-checkbox-service-generate-report-unit"])
@pytest.mark.feature("checkbox")
def test_checkbox_generate_report_unit_exists(file):
    """Test that generate-report.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/generate-report.service")


@pytest.mark.testcov(["GL-TESTCOV-checkbox-service-getty-tty1-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_getty_tty1_service_disabled(systemd: Systemd):
    """Test that getty@tty1.service is disabled"""
    assert systemd.is_disabled("getty@tty1.service")


@pytest.mark.testcov(["GL-TESTCOV-checkbox-service-getty-tty1-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_getty_tty1_service_inactive(systemd: Systemd):
    """Test that getty@tty1.service is inactive"""
    assert systemd.is_inactive("getty@tty1.service")


@pytest.mark.testcov(["GL-TESTCOV-checkbox-service-getty-tty1-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_serial_getty_service_disabled(systemd: Systemd):
    """Test that serial-getty@.service is disabled"""
    assert systemd.is_disabled("serial-getty@.service")


@pytest.mark.testcov(["GL-TESTCOV-checkbox-service-serial-getty-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_serial_getty_service_inactive(systemd: Systemd):
    """Test that serial-getty@.service is inactive"""
    assert systemd.is_inactive("serial-getty@.service")


@pytest.mark.testcov(["GL-TESTCOV-checkbox-service-nginx-enable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_nginx_service_enabled(systemd: Systemd):
    """Test that nginx.service is enabled"""
    assert systemd.is_enabled("nginx.service")


@pytest.mark.testcov(["GL-TESTCOV-checkbox-service-nginx-enable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_nginx_service_active(systemd: Systemd):
    """Test that nginx.service is active"""
    assert systemd.is_active("nginx.service")


# =============================================================================
# chost Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-chost-service-apparmor-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.testcov(["GL-TESTCOV-chost-service-apparmor-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


@pytest.mark.testcov(["GL-TESTCOV-chost-service-containerd-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_containerd_service_enabled(systemd: Systemd):
    """Test that containerd.service is enabled"""
    assert systemd.is_enabled("containerd.service")


@pytest.mark.testcov(["GL-TESTCOV-chost-service-containerd-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_containerd_service_active(systemd: Systemd):
    """Test that containerd.service is active"""
    assert systemd.is_active("containerd.service")


# TODO: Add tests for user-level systemd units
# @pytest.mark.testcov(["GL-TESTCOV-chost-service-user-dbus-socket-enable"])
# @pytest.mark.feature("chost")
# @pytest.mark.booted(reason="Requires systemd")
# def test_chost_dbus_socket_user_service_enabled(systemd: Systemd):
#     """Test that user service for dbus.socket is enabled"""
#     assert systemd.is_enabled_user("dbus.socket")
#
#
# @pytest.mark.testcov(["GL-TESTCOV-chost-service-user-dbus-socket-enable"])
# @pytest.mark.feature("chost")
# @pytest.mark.booted(reason="Requires systemd")
# def test_chost_dbus_socket_user_service_active(systemd: Systemd):
#     """Test that user service for dbus.socket is active"""
#     assert systemd.is_active_user("dbus.socket")


# -----------------------------------------------------------------------------
# cisSshd Feature Unit Files
# -----------------------------------------------------------------------------


@pytest.mark.testcov(["GL-TESTCOV-cisSshd-service-gardenlinux-fw-ipv4-unit"])
@pytest.mark.feature("cisSshd")
def test_cissshd_fw_ipv4_unit_exists(file):
    """Test that gardenlinux-fw-ipv4.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv4.service")


@pytest.mark.testcov(["GL-TESTCOV-cisSshd-service-gardenlinux-fw-ipv6-unit"])
@pytest.mark.feature("cisSshd")
def test_cissshd_fw_ipv6_unit_exists(file):
    """Test that gardenlinux-fw-ipv6.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv6.service")


# =============================================================================
# clamav Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-clamav-service-clamav-enable"])
@pytest.mark.feature("clamav")
@pytest.mark.booted(reason="Requires systemd")
def test_clamav_clamav_daemon_service_enabled(systemd: Systemd):
    """Test that clamav-daemon.service is enabled"""
    assert systemd.is_enabled("clamav-daemon.service")


@pytest.mark.testcov(["GL-TESTCOV-clamav-service-clamav-enable"])
@pytest.mark.feature("clamav")
@pytest.mark.booted(reason="Requires systemd")
def test_clamav_clamav_daemon_service_active(systemd: Systemd):
    """Test that clamav-daemon.service is active"""
    assert systemd.is_active("clamav-daemon.service")


# =============================================================================
# fedramp Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-gardenlinux-fw-ipv4-unit"])
@pytest.mark.feature("fedramp")
def test_fedramp_fw_ipv4_unit_exists(file):
    """Test that gardenlinux-fw-ipv4.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv4.service")


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-gardenlinux-fw-ipv6-unit"])
@pytest.mark.feature("fedramp")
def test_fedramp_fw_ipv6_unit_exists(file):
    """Test that gardenlinux-fw-ipv6.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv6.service")


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-apparmor-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-apparmor-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-gardenlinux-fw-ipv4-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv4_service_enabled(systemd: Systemd):
    """Test that gardenlinux-fw-ipv4.service is enabled"""
    assert systemd.is_enabled("gardenlinux-fw-ipv4.service")


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-gardenlinux-fw-ipv4-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv4_service_active(systemd: Systemd):
    """Test that gardenlinux-fw-ipv4.service is active"""
    assert systemd.is_active("gardenlinux-fw-ipv4.service")


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-gardenlinux-fw-ipv6-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv6_service_enabled(systemd: Systemd):
    """Test that gardenlinux-fw-ipv6.service is enabled"""
    assert systemd.is_enabled("gardenlinux-fw-ipv6.service")


@pytest.mark.testcov(["GL-TESTCOV-fedramp-service-gardenlinux-fw-ipv6-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv6_service_active(systemd: Systemd):
    """Test that gardenlinux-fw-ipv6.service is active"""
    assert systemd.is_active("gardenlinux-fw-ipv6.service")


# =============================================================================
# firewall Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-firewall-service-nftables-enable"])
@pytest.mark.feature("firewall")
@pytest.mark.booted(reason="Requires systemd")
def test_firewall_nftables_service_enabled(systemd: Systemd):
    """Test that nftables.service is enabled"""
    assert systemd.is_enabled("nftables.service")


@pytest.mark.testcov(["GL-TESTCOV-firewall-service-nftables-enable"])
@pytest.mark.feature("firewall")
@pytest.mark.booted(reason="Requires systemd")
def test_firewall_nftables_service_active(systemd: Systemd):
    """Test that nftables.service is active"""
    assert systemd.is_active("nftables.service")


# =============================================================================
# gcp Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-gcp-service-google-guest-agent-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_google_guest_agent_service_enabled(systemd: Systemd):
    """Test that google-guest-agent.service is enabled"""
    assert systemd.is_enabled("google-guest-agent.service")


@pytest.mark.testcov(["GL-TESTCOV-gcp-service-google-guest-agent-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu", reason="google-guest-agent.service crashes if run in qemu"
)
def test_gcp_google_guest_agent_service_active(systemd: Systemd):
    """Test that google-guest-agent.service is active"""
    assert systemd.is_active("google-guest-agent.service")


@pytest.mark.testcov(["GL-TESTCOV-gcp-service-no-irqbalance"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_no_irqbalance_service(systemd: Systemd):
    """Test that irqbalance.service is not installed"""
    assert not any(
        u.unit == "irqbalance.service" for u in systemd.list_installed_units()
    )


# =============================================================================
# gdch Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-gdch-service-no-irqbalance"])
@pytest.mark.feature("gdch")
@pytest.mark.booted(reason="Requires systemd")
def test_gdch_no_irqbalance_service(systemd: Systemd):
    """Test that irqbalance.service is not installed"""
    assert not any(
        u.unit == "irqbalance.service" for u in systemd.list_installed_units()
    )


# =============================================================================
# iscsi Feature Services
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-iscsi-service-iscsi-initiatorname-unit",
    ]
)
@pytest.mark.feature("iscsi")
def test_iscsi_initiatorname_template_exists(file: File):
    """Test that iSCSI initiator name template exists"""
    assert file.exists(
        "/etc/systemd/system/iscsi-initiatorname.service"
    ), "iSCSI initiator name service template should exist"


@pytest.mark.testcov(["GL-TESTCOV-iscsi-service-iscsi-initiatorname-unit"])
@pytest.mark.feature("iscsi")
def test_iscsi_initiatorname_unit_exists(file):
    """Test that iscsi-initiatorname.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/iscsi-initiatorname.service")


@pytest.mark.testcov(["GL-TESTCOV-iscsi-service-iscsid-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_iscsid_service_enabled(systemd: Systemd):
    """Test that iscsid.service is enabled"""
    assert systemd.is_enabled("iscsid.service")


@pytest.mark.testcov(["GL-TESTCOV-iscsi-service-iscsid-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_iscsid_service_active(systemd: Systemd):
    """Test that iscsid.service is active"""
    assert systemd.is_active("iscsid.service")


@pytest.mark.testcov(["GL-TESTCOV-iscsi-service-tgt-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_tgt_service_enabled(systemd: Systemd):
    """Test that tgt.service is enabled"""
    assert systemd.is_enabled("tgt.service")


@pytest.mark.testcov(["GL-TESTCOV-iscsi-service-tgt-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_tgt_service_active(systemd: Systemd):
    """Test that tgt.service is active"""
    assert systemd.is_active("tgt.service")


# =============================================================================
# khost Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-khost-service-apparmor-enable"])
@pytest.mark.feature("khost")
@pytest.mark.booted(reason="Requires systemd")
def test_khost_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.testcov(["GL-TESTCOV-khost-service-apparmor-enable"])
@pytest.mark.feature("khost")
@pytest.mark.booted(reason="Requires systemd")
def test_khost_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


# =============================================================================
# lima Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-lima-service-sshd-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_ssh_service_enabled(systemd: Systemd):
    """Test that ssh.service is enabled"""
    assert systemd.is_enabled("ssh.service")


@pytest.mark.testcov(["GL-TESTCOV-lima-service-sshd-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_ssh_service_active(systemd: Systemd):
    """Test that ssh.service is active"""
    assert systemd.is_active("ssh.service")


# =============================================================================
# metal Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-metal-service-ipmievd-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_ipmievd_service_enabled(systemd: Systemd):
    """Test that ipmievd.service is enabled"""
    assert systemd.is_enabled("ipmievd.service")


@pytest.mark.testcov(["GL-TESTCOV-metal-service-ipmievd-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu", reason="IPMI device is not available on QEMU and service will fail"
)
def test_metal_ipmievd_service_active(systemd: Systemd):
    """Test that ipmievd.service is active"""
    assert systemd.is_active("ipmievd.service")


@pytest.mark.testcov(["GL-TESTCOV-metal-service-mdmonitor-oneshot-timer-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_mdmonitor_oneshot_timer_enabled(systemd: Systemd):
    """Test that mdadm.service is enabled"""
    assert systemd.is_enabled("mdmonitor-oneshot.timer")


@pytest.mark.testcov(["GL-TESTCOV-metal-service-mdmonitor-oneshot-timer-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_mdmonitor_oneshot_timer_inactive(systemd: Systemd):
    """Test that mdmonitor-oneshot.timer is inactive"""
    assert systemd.is_inactive("mdmonitor-oneshot.timer")


@pytest.mark.testcov(["GL-TESTCOV-metal-service-smartmontools-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu",
    reason="unit will has condition to not be enabled/started on virtualization",
)
def test_metal_smartd_service_enabled(systemd: Systemd):
    """Test that smartd.service is enabled"""
    assert systemd.is_enabled("smartd.service")


@pytest.mark.testcov(["GL-TESTCOV-metal-service-smartmontools-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu",
    reason="unit will has condition to not be enabled/started on virtualization",
)
def test_metal_smartd_service_active(systemd: Systemd):
    """Test that smartd.service is active"""
    assert systemd.is_active("smartd.service")


# =============================================================================
# multipath Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-multipath-service-multipathd-enable"])
@pytest.mark.feature("multipath")
@pytest.mark.booted(reason="Requires systemd")
def test_multipath_multipathd_service_enabled(systemd: Systemd):
    """Test that multipathd.service is enabled"""
    assert systemd.is_enabled("multipathd.service")


@pytest.mark.testcov(["GL-TESTCOV-multipath-service-multipathd-enable"])
@pytest.mark.feature("multipath")
@pytest.mark.booted(reason="Requires systemd")
def test_multipath_multipathd_service_active(systemd: Systemd):
    """Test that multipathd.service is active"""
    assert systemd.is_active("multipathd.service")


# -----------------------------------------------------------------------------
# nvme Feature Unit Files
# -----------------------------------------------------------------------------


@pytest.mark.testcov(["GL-TESTCOV-nvme-service-nvme-hostid-unit"])
@pytest.mark.feature("nvme")
def test_nvme_hostid_unit_exists(file):
    """Test that nvme-hostid.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/nvme-hostid.service")


# =============================================================================
# openstackMetal Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-openstackMetal-service-netplan-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackMetal_systemd_networkd_service_enabled(systemd: Systemd):
    """Test that systemd-networkd.service is enabled"""
    assert systemd.is_enabled("systemd-networkd.service")


@pytest.mark.testcov(["GL-TESTCOV-openstackMetal-service-netplan-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackMetal_systemd_networkd_service_active(systemd: Systemd):
    """Test that systemd-networkd.service is active"""
    assert systemd.is_active("systemd-networkd.service")


# =============================================================================
# sap Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-sap-service-auditd-enable"])
@pytest.mark.feature("sap")
@pytest.mark.booted(reason="Requires systemd")
def test_sap_auditd_service_enabled(systemd: Systemd):
    """Test that auditd.service is enabled"""
    assert systemd.is_enabled("auditd.service")


@pytest.mark.testcov(["GL-TESTCOV-sap-service-auditd-enable"])
@pytest.mark.feature("sap")
@pytest.mark.booted(reason="Requires systemd")
def test_sap_auditd_service_active(systemd: Systemd):
    """Test that auditd.service is active"""
    assert systemd.is_active("auditd.service")


# =============================================================================
# server Feature Services
# =============================================================================


@pytest.mark.testcov(
    [
        "GL-TESTCOV-server-config-service-systemd-coredump-override",
    ]
)
@pytest.mark.feature("server and not _prod")
def test_server_systemd_coredump_override_exists(file: File):
    """Test that systemd-coredump service override exists"""
    assert file.exists("/etc/systemd/system/systemd-coredump@.service.d/override.conf")


@pytest.mark.testcov(["GL-TESTCOV-server-service-systemd-coredump-enable"])
@pytest.mark.feature("server and not _prod")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_coredump_socket_active(systemd: Systemd):
    """Test that systemd-coredump.socket is enabled"""
    assert systemd.is_active("systemd-coredump.socket")


@pytest.mark.testcov(["GL-TESTCOV-server-service-kexec-load-unit"])
@pytest.mark.feature("server")
def test_server_kexec_load_unit_exists(file):
    """Test that kexec-load@.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/kexec-load@.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-cron-update-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_cron_update_service_inactive(systemd: Systemd):
    """Test that cron-update.service is inactive (oneshot service)"""
    assert systemd.is_inactive("cron-update.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-kexec-load-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_kexec_load_service_enabled(
    systemd: Systemd, kernel_versions: KernelVersions
):
    kernel_version = kernel_versions.get_running().version
    """Test that kexec-load@{kernel_version}.service is enabled"""
    assert systemd.is_enabled(f"kexec-load@{kernel_version}.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-kexec-load-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_kexec_load_service_inactive(
    systemd: Systemd, kernel_versions: KernelVersions
):
    kernel_version = kernel_versions.get_running().version
    """Test that kexec-load@{kernel_version}.service is inactive (oneshot service)"""
    assert systemd.is_inactive(f"kexec-load@{kernel_version}.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-sysstat-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_sysstat_service_enabled(systemd: Systemd):
    """Test that sysstat.service is enabled"""
    assert systemd.is_enabled("sysstat.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-sysstat-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_sysstat_service_active(systemd: Systemd):
    """Test that sysstat.service is active"""
    assert systemd.is_active("sysstat.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-systemd-networkd-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_networkd_service_enabled(systemd: Systemd):
    """Test that systemd-networkd.service is enabled"""
    assert systemd.is_enabled("systemd-networkd.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-systemd-networkd-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_networkd_service_active(systemd: Systemd):
    """Test that systemd-networkd.service is active"""
    assert systemd.is_active("systemd-networkd.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-systemd-repart-socket-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_repart_socket_active(systemd: Systemd):
    """Test that systemd-repart.socket is enabled"""
    assert systemd.is_active("systemd-repart.socket")


@pytest.mark.testcov(["GL-TESTCOV-server-service-systemd-resolved-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_resolved_service_enabled(systemd: Systemd):
    """Test that systemd-resolved.service is enabled"""
    assert systemd.is_enabled("systemd-resolved.service")


@pytest.mark.testcov(["GL-TESTCOV-server-service-systemd-resolved-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_resolved_service_active(systemd: Systemd):
    """Test that systemd-resolved.service is active"""
    assert systemd.is_active("systemd-resolved.service")


# =============================================================================
# ssh Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-ssh-service-ssh-keygen-unit"])
@pytest.mark.feature("ssh")
def test_ssh_keygen_unit_exists(file):
    """Test that ssh-keygen.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ssh-keygen.service")


@pytest.mark.testcov(["GL-TESTCOV-ssh-service-ssh-moduli-unit"])
@pytest.mark.feature("ssh")
def test_ssh_moduli_unit_exists(file):
    """Test that ssh-moduli.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ssh-moduli.service")


@pytest.mark.testcov(
    [
        "GL-TESTCOV-ssh-service-ssh-enable",
        "GL-TESTCOV-ssh-service-ssh-socket-preset-disable",
    ]
)
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_socket_disabled(systemd: Systemd):
    """Test that ssh.socket is disabled by preset"""
    assert systemd.is_disabled("ssh.socket")


@pytest.mark.testcov(
    [
        "GL-TESTCOV-ssh-service-ssh-enable",
        "GL-TESTCOV-ssh-service-ssh-socket-preset-disable",
    ]
)
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_socket_inactive(systemd: Systemd):
    """Test that ssh.service is inactive"""
    assert systemd.is_inactive("ssh.socket")


# TODO: enable if nftables or iptables is not available
# see: features/ssh/exec.config
# @pytest.mark.testcov([
#     "GL-TESTCOV-ssh-service-sshguard-enable",
#     "GL-TESTCOV-ssh-service-sshguard-preset-disable"
#     ])
# @pytest.mark.feature("ssh")
# @pytest.mark.booted(reason="Requires systemd")
# def test_ssh_sshguard_service_disabled(systemd: Systemd):
#     """Test that sshguard.service is disabled by preset"""
#     assert systemd.is_disabled("sshguard.service")
#
#
# @pytest.mark.testcov([
#     "GL-TESTCOV-ssh-service-sshguard-enable",
#     "GL-TESTCOV-ssh-service-sshguard-preset-disable"
#     ])
# @pytest.mark.feature("ssh")
# @pytest.mark.booted(reason="Requires systemd")
# def test_ssh_sshguard_service_inactive(systemd: Systemd):
#     """Test that sshguard.service is inactive"""
#     assert systemd.is_inactive("sshguard.service")


@pytest.mark.testcov(["GL-TESTCOV-ssh-service-ssh-keygen-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_keygen_service_enabled(systemd: Systemd):
    """Test that ssh-keygen.service is enabled"""
    assert systemd.is_enabled("ssh-keygen.service")


@pytest.mark.testcov(["GL-TESTCOV-ssh-service-ssh-keygen-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_keygen_service_active(systemd: Systemd):
    """Test that ssh-keygen.service is active"""
    assert systemd.is_active("ssh-keygen.service")


@pytest.mark.testcov(["GL-TESTCOV-ssh-service-sshguard-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_sshguard_service_enabled(systemd: Systemd):
    """Test that sshguard.service is enabled"""
    assert systemd.is_enabled("sshguard.service")


@pytest.mark.testcov(["GL-TESTCOV-ssh-service-sshguard-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu", reason="a started sshguard prevents running the testsuite"
)
def test_ssh_sshguard_service_active(systemd: Systemd):
    """Test that sshguard.service is active"""
    assert systemd.is_active("sshguard.service")


# =============================================================================
# vhost Feature Services
# =============================================================================


@pytest.mark.testcov(["GL-TESTCOV-vhost-service-libvirtd-socket-enable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_socket_service_enabled(systemd: Systemd):
    """Test that libvirtd.socket is enabled"""
    assert systemd.is_enabled("libvirtd.socket")


@pytest.mark.testcov(["GL-TESTCOV-vhost-service-libvirtd-socket-enable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_socket_service_active(systemd: Systemd):
    """Test that libvirtd.socket is active"""
    assert systemd.is_active("libvirtd.socket")


@pytest.mark.testcov(["GL-TESTCOV-vhost-service-libvirtd-tls-socket-preset-disable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_tls_socket_service_disabled(systemd: Systemd):
    """Test that libvirtd-tls.socket is disabled by preset"""
    assert systemd.is_disabled("libvirtd-tls.socket")


@pytest.mark.testcov(["GL-TESTCOV-vhost-service-libvirtd-tls-socket-preset-disable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_tls_socket_service_inactive(systemd: Systemd):
    """Test that libvirtd-tls.socket is inactive"""
    assert systemd.is_inactive("libvirtd-tls.socket")
