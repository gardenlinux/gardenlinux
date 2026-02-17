"""
Test systemd services for enabled/disabled, active/inactive states across all Garden Linux features.
"""

import pytest
from plugins.file import File
from plugins.initrd import Initrd
from plugins.kernel_versions import KernelVersions
from plugins.modify import allow_system_modifications
from plugins.parse_file import ParseFile
from plugins.systemd import Systemd

# =============================================================================
# _ephemeral Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_ephemeral-service-initrd-ephemeral-cryptsetup-unit"])
@pytest.mark.feature("_ephemeral")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_ephemeral_check_initrd_cryptsetup_unit_exists(initrd: Initrd):
    """Test that ephemeral-cryptsetup.service unit file exists in initrd"""
    assert initrd.contains_file("etc/systemd/system/ephemeral-cryptsetup.service")


# =============================================================================
# _fwcfg Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_fwcfg-service-qemu-fw_cfg-script-unit"])
@pytest.mark.feature("_fwcfg")
def test_fwcfg_qemu_fw_cfg_script_unit_exists(file):
    """Test that qemu-fw_cfg-script.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/qemu-fw_cfg-script.service")


@pytest.mark.setting_ids(["GL-SET-_fwcfg-service-qemu-fw_cfg-script-enable"])
@pytest.mark.feature("_fwcfg")
@pytest.mark.booted(reason="Requires systemd")
def test__fwcfg_qemu_fw_cfg_script_service_enabled(systemd: Systemd):
    """Test that qemu-fw_cfg-script.service is enabled"""
    assert systemd.is_enabled("qemu-fw_cfg-script.service")


@pytest.mark.setting_ids(["GL-SET-_fwcfg-service-qemu-fw_cfg-script-enable"])
@pytest.mark.feature("_fwcfg")
@pytest.mark.booted(reason="Requires systemd")
def test__fwcfg_qemu_fw_cfg_script_service_active(systemd: Systemd):
    """Test that qemu-fw_cfg-script.service is active"""
    assert systemd.is_active("qemu-fw_cfg-script.service")


# =============================================================================
# _kdump Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_kdump-service-kdump-tools-enable"])
@pytest.mark.feature("_kdump")
@pytest.mark.booted(reason="Requires systemd")
def test__kdump_kdump_tools_service_enabled(systemd: Systemd):
    """Test that kdump-tools.service is enabled"""
    assert systemd.is_enabled("kdump-tools.service")


@pytest.mark.setting_ids(["GL-SET-_kdump-service-kdump-tools-enable"])
@pytest.mark.feature("_kdump")
@pytest.mark.booted(reason="Requires systemd")
def test__kdump_kdump_tools_service_active(systemd: Systemd):
    """Test that kdump-tools.service is active"""
    assert systemd.is_active("kdump-tools.service")


# =============================================================================
# _prod Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_prod-service-no-systemd-coredump"])
@pytest.mark.feature("_prod")
@pytest.mark.booted(reason="Requires systemd")
def test__prod_no_systemd_coredump_service(systemd: Systemd):
    """Test that systemd-coredump.service is not installed"""
    assert not any(
        u.unit == "systemd-coredump.service" for u in systemd.list_installed_units()
    )


# =============================================================================
# _pxe Feature Services
# =============================================================================


@pytest.mark.setting_ids(
    ["GL-SET-_pxe-config-initrd-module-gardenlinux-live-gl-end-unit"]
)
@pytest.mark.feature("_pxe")
def test_pxe_gl_end_unit_exists(file):
    """Test that gl-end.service unit file exists"""
    assert file.is_regular_file(
        "/usr/lib/dracut/modules.d/98gardenlinux-live/gl-end.service"
    )


# =============================================================================
# _tpm2 Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_tpm2-service-initrd-check-tpm-unit"])
@pytest.mark.feature("_tpm2")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_tpm2_check_initrd_tpm_unit_exists(initrd: Initrd):
    """Test that check-tpm.service unit file exists in initrd"""
    assert initrd.contains_file("etc/systemd/system/check-tpm.service")


@pytest.mark.setting_ids(["GL-SET-_tpm2-service-initrd-systemd-repart-check-tpm-unit"])
@pytest.mark.feature("_tpm2")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_tpm2_check_initrd_systemd_repart_requires_check_tpm_unit(initrd: Initrd):
    """Test that check-tpm.service unit file exists in initrd systemd-repart.service.requires"""
    assert initrd.contains_file(
        "etc/systemd/system/systemd-repart.service.requires/check-tpm.service"
    )


@pytest.mark.setting_ids(["GL-SET-_tpm2-service-initrd-tpm2-measure-unit"])
@pytest.mark.feature("_tpm2")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_tpm2_check_initrd_tpm2_measure_unit_exists(initrd: Initrd):
    """Test that tpm2-measure.service unit file exists"""
    assert initrd.contains_file("etc/systemd/system/tpm2-measure.service")


@pytest.mark.setting_ids(["GL-SET-_tpm2-service-initrd-switch-root-tpm2-measure-unit"])
@pytest.mark.feature("_tpm2")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_tpm2_check_initrd_switch_root_requires_tpm2_measure_unit(initrd: Initrd):
    """Test that tpm2-measure.service unit file exists in initrd initrd-switch-root.target.requires"""
    assert initrd.contains_file(
        "etc/systemd/system/initrd-switch-root.target.requires/tpm2-measure.service"
    )


@pytest.mark.setting_ids(["GL-SET-_tpm2-service-initrd-systemd-cryptsetup-var-unit"])
@pytest.mark.feature("_tpm2")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_tpm2_check_initrd_systemd_cryptsetup_var_unit_exists(initrd: Initrd):
    """Test that systemd-cryptsetup-var.service unit file exists in initrd"""
    assert initrd.contains_file("etc/systemd/system/systemd-cryptsetup-var.service")


# =============================================================================
# _trustedboot Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_trustedboot-service-initrd-emergency-unit"])
@pytest.mark.feature("_trustedboot")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_trustedboot_check_initrd_emergency_unit_exists(initrd: Initrd):
    """Test that emergency.service unit file exists in initrd"""
    assert initrd.contains_file("etc/systemd/system/emergency.service")


@pytest.mark.setting_ids(
    [
        "GL-SET-_trustedboot-service-initrd-local-fs-target-requires-check-secureboot-unit"
    ]
)
@pytest.mark.feature("_trustedboot")
@pytest.mark.root(reason="Reading the initrd contents requires root access")
@pytest.mark.booted(reason="Chroot environments have no initrd")
def test_trustedboot_check_initrd_local_fs_target_requires_check_secureboot_unit(
    initrd: Initrd,
):
    """Test that check-secureboot.service unit file exists in local-fs.target.requires"""
    assert initrd.contains_file(
        "etc/systemd/system/local-fs.target.requires/check-secureboot.service"
    )


# =============================================================================
# aws Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-aws-service-aws-clocksource-unit"])
@pytest.mark.feature("aws")
def test_aws_clocksource_unit_exists(file):
    """Test that aws-clocksource.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/aws-clocksource.service")


@pytest.mark.setting_ids(["GL-SET-aws-service-aws-clocksource-enable"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_aws_clocksource_service_enabled(systemd: Systemd):
    """Test that aws-clocksource.service is enabled"""
    assert systemd.is_enabled("aws-clocksource.service")


@pytest.mark.setting_ids(["GL-SET-aws-service-aws-clocksource-enable"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_aws_clocksource_service_inactive(systemd: Systemd):
    """Test that aws-clocksource.service is inactive (oneshot service)"""
    assert systemd.is_inactive("aws-clocksource.service")


# =============================================================================
# checkbox Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-checkbox-service-generate-report-unit"])
@pytest.mark.feature("checkbox")
def test_checkbox_generate_report_unit_exists(file):
    """Test that generate-report.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/generate-report.service")


@pytest.mark.setting_ids(["GL-SET-checkbox-service-getty-tty1-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_getty_tty1_service_disabled(systemd: Systemd):
    """Test that getty@tty1.service is disabled"""
    assert systemd.is_disabled("getty@tty1.service")


@pytest.mark.setting_ids(["GL-SET-checkbox-service-getty-tty1-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_getty_tty1_service_inactive(systemd: Systemd):
    """Test that getty@tty1.service is inactive"""
    assert systemd.is_inactive("getty@tty1.service")


@pytest.mark.setting_ids(["GL-SET-checkbox-service-getty-tty1-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_serial_getty_service_disabled(systemd: Systemd):
    """Test that serial-getty@.service is disabled"""
    assert systemd.is_disabled("serial-getty@.service")


@pytest.mark.setting_ids(["GL-SET-checkbox-service-serial-getty-disable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_serial_getty_service_inactive(systemd: Systemd):
    """Test that serial-getty@.service is inactive"""
    assert systemd.is_inactive("serial-getty@.service")


@pytest.mark.setting_ids(["GL-SET-checkbox-service-nginx-enable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_nginx_service_enabled(systemd: Systemd):
    """Test that nginx.service is enabled"""
    assert systemd.is_enabled("nginx.service")


@pytest.mark.setting_ids(["GL-SET-checkbox-service-nginx-enable"])
@pytest.mark.feature("checkbox")
@pytest.mark.booted(reason="Requires systemd")
def test_checkbox_nginx_service_active(systemd: Systemd):
    """Test that nginx.service is active"""
    assert systemd.is_active("nginx.service")


# =============================================================================
# chost Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-chost-service-apparmor-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.setting_ids(["GL-SET-chost-service-apparmor-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


@pytest.mark.setting_ids(["GL-SET-chost-service-containerd-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_containerd_service_enabled(systemd: Systemd):
    """Test that containerd.service is enabled"""
    assert systemd.is_enabled("containerd.service")


@pytest.mark.setting_ids(["GL-SET-chost-service-containerd-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_containerd_service_active(systemd: Systemd):
    """Test that containerd.service is active"""
    assert systemd.is_active("containerd.service")


# TODO: Add tests for user-level systemd units
# @pytest.mark.setting_ids(["GL-SET-chost-service-user-dbus-socket-enable"])
# @pytest.mark.feature("chost")
# @pytest.mark.booted(reason="Requires systemd")
# def test_chost_dbus_socket_user_service_enabled(systemd: Systemd):
#     """Test that user service for dbus.socket is enabled"""
#     assert systemd.is_enabled_user("dbus.socket")
#
#
# @pytest.mark.setting_ids(["GL-SET-chost-service-user-dbus-socket-enable"])
# @pytest.mark.feature("chost")
# @pytest.mark.booted(reason="Requires systemd")
# def test_chost_dbus_socket_user_service_active(systemd: Systemd):
#     """Test that user service for dbus.socket is active"""
#     assert systemd.is_active_user("dbus.socket")


# -----------------------------------------------------------------------------
# cisSshd Feature Unit Files
# -----------------------------------------------------------------------------


@pytest.mark.setting_ids(["GL-SET-cisSshd-service-gardenlinux-fw-ipv4-unit"])
@pytest.mark.feature("cisSshd")
def test_cissshd_fw_ipv4_unit_exists(file):
    """Test that gardenlinux-fw-ipv4.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv4.service")


@pytest.mark.setting_ids(["GL-SET-cisSshd-service-gardenlinux-fw-ipv6-unit"])
@pytest.mark.feature("cisSshd")
def test_cissshd_fw_ipv6_unit_exists(file):
    """Test that gardenlinux-fw-ipv6.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv6.service")


# =============================================================================
# clamav Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-clamav-service-clamav-enable"])
@pytest.mark.feature("clamav")
@pytest.mark.booted(reason="Requires systemd")
def test_clamav_clamav_daemon_service_enabled(systemd: Systemd):
    """Test that clamav-daemon.service is enabled"""
    assert systemd.is_enabled("clamav-daemon.service")


@pytest.mark.setting_ids(["GL-SET-clamav-service-clamav-enable"])
@pytest.mark.feature("clamav")
@pytest.mark.booted(reason="Requires systemd")
def test_clamav_clamav_daemon_service_active(systemd: Systemd):
    """Test that clamav-daemon.service is active"""
    assert systemd.is_active("clamav-daemon.service")


# =============================================================================
# fedramp Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-fedramp-service-gardenlinux-fw-ipv4-unit"])
@pytest.mark.feature("fedramp")
def test_fedramp_fw_ipv4_unit_exists(file):
    """Test that gardenlinux-fw-ipv4.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv4.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-gardenlinux-fw-ipv6-unit"])
@pytest.mark.feature("fedramp")
def test_fedramp_fw_ipv6_unit_exists(file):
    """Test that gardenlinux-fw-ipv6.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/gardenlinux-fw-ipv6.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-apparmor-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-apparmor-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-gardenlinux-fw-ipv4-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv4_service_enabled(systemd: Systemd):
    """Test that gardenlinux-fw-ipv4.service is enabled"""
    assert systemd.is_enabled("gardenlinux-fw-ipv4.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-gardenlinux-fw-ipv4-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv4_service_active(systemd: Systemd):
    """Test that gardenlinux-fw-ipv4.service is active"""
    assert systemd.is_active("gardenlinux-fw-ipv4.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-gardenlinux-fw-ipv6-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv6_service_enabled(systemd: Systemd):
    """Test that gardenlinux-fw-ipv6.service is enabled"""
    assert systemd.is_enabled("gardenlinux-fw-ipv6.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-gardenlinux-fw-ipv6-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_gardenlinux_fw_ipv6_service_active(systemd: Systemd):
    """Test that gardenlinux-fw-ipv6.service is active"""
    assert systemd.is_active("gardenlinux-fw-ipv6.service")


# =============================================================================
# firewall Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-firewall-service-nftables-enable"])
@pytest.mark.feature("firewall")
@pytest.mark.booted(reason="Requires systemd")
def test_firewall_nftables_service_enabled(systemd: Systemd):
    """Test that nftables.service is enabled"""
    assert systemd.is_enabled("nftables.service")


@pytest.mark.setting_ids(["GL-SET-firewall-service-nftables-enable"])
@pytest.mark.feature("firewall")
@pytest.mark.booted(reason="Requires systemd")
def test_firewall_nftables_service_active(systemd: Systemd):
    """Test that nftables.service is active"""
    assert systemd.is_active("nftables.service")


# =============================================================================
# gardener Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gardener-service-apparmor-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.setting_ids(["GL-SET-gardener-service-apparmor-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


@pytest.mark.setting_ids(
    [
        "GL-SET-gardener-service-containerd-enable",
        "GL-SET-gardener-service-containerd-disable",
    ]
)
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_containerd_service_disabled(systemd: Systemd):
    """Test that containerd.service is disabled"""
    assert systemd.is_disabled("containerd.service")


@pytest.mark.setting_ids(
    [
        "GL-SET-gardener-service-containerd-enable",
        "GL-SET-gardener-service-containerd-disable",
    ]
)
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_containerd_service_inactive(systemd: Systemd):
    """Test that containerd.service is inactive"""
    assert systemd.is_inactive("containerd.service")


@pytest.mark.setting_ids(["GL-SET-gardener-service-logrotate-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_logrotate_timer_service_enabled(systemd: Systemd):
    """Test that logrotate.timer is enabled"""
    assert systemd.is_enabled("logrotate.timer")


@pytest.mark.setting_ids(["GL-SET-gardener-service-logrotate-enable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_logrotate_timer_service_active(systemd: Systemd):
    """Test that logrotate.timer is active"""
    assert systemd.is_active("logrotate.timer")


@pytest.mark.setting_ids(["GL-SET-gardener-service-ssh-disable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_ssh_service_disabled(systemd: Systemd):
    """Test that ssh.service is disabled"""
    # TODO: find better way to exclude this
    if allow_system_modifications():
        pytest.skip("ssh.service is enabled to connect to test instances")
    else:
        assert systemd.is_disabled("ssh.service")


@pytest.mark.setting_ids(["GL-SET-gardener-service-ssh-disable"])
@pytest.mark.feature("gardener")
@pytest.mark.booted(reason="Requires systemd")
def test_gardener_ssh_service_inactive(systemd: Systemd):
    """Test that ssh.service is inactive"""
    # TODO: find better way to exclude this
    if allow_system_modifications():
        pytest.skip("ssh.service is enabled to connect to test instances")
    else:
        assert systemd.is_inactive("ssh.service")


@pytest.mark.setting_ids(
    [
        "GL-SET-gardener-config-containerd-override",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_containerd_override_exists(file: File):
    """Test that gardener containerd service override exists"""
    assert file.exists(
        "/etc/systemd/system/containerd.service.d/override.conf"
    ), "Gardener containerd service override should exist"


@pytest.mark.setting_ids(
    [
        "GL-SET-gardener-config-containerd-override",
    ]
)
@pytest.mark.feature("gardener")
def test_gardener_containerd_override_content(parse_file: ParseFile):
    """Test that gardener containerd service override contains the correct content"""
    config = parse_file.parse(
        "/etc/systemd/system/containerd.service.d/override.conf", format="ini"
    )
    assert (
        config["Service"]["LimitMEMLOCK"] == "67108864"
    ), "Gardener containerd service override should include correct LimitMEMLOCK value"
    assert (
        config["Service"]["LimitNOFILE"] == "1048576"
    ), "Gardener containerd service override should include correct LimitNOFILE value"


# =============================================================================
# gcp Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-gcp-service-google-guest-agent-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_google_guest_agent_service_enabled(systemd: Systemd):
    """Test that google-guest-agent.service is enabled"""
    assert systemd.is_enabled("google-guest-agent.service")


@pytest.mark.setting_ids(["GL-SET-gcp-service-google-guest-agent-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu", reason="google-guest-agent.service crashes if run in qemu"
)
def test_gcp_google_guest_agent_service_active(systemd: Systemd):
    """Test that google-guest-agent.service is active"""
    assert systemd.is_active("google-guest-agent.service")


@pytest.mark.setting_ids(["GL-SET-gcp-service-no-irqbalance"])
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


@pytest.mark.setting_ids(["GL-SET-gdch-service-no-irqbalance"])
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


@pytest.mark.setting_ids(
    [
        "GL-SET-iscsi-service-iscsi-initiatorname-unit",
    ]
)
@pytest.mark.feature("iscsi")
def test_iscsi_initiatorname_template_exists(file: File):
    """Test that iSCSI initiator name template exists"""
    assert file.exists(
        "/etc/systemd/system/iscsi-initiatorname.service"
    ), "iSCSI initiator name service template should exist"


@pytest.mark.setting_ids(["GL-SET-iscsi-service-iscsi-initiatorname-unit"])
@pytest.mark.feature("iscsi")
def test_iscsi_initiatorname_unit_exists(file):
    """Test that iscsi-initiatorname.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/iscsi-initiatorname.service")


@pytest.mark.setting_ids(["GL-SET-iscsi-service-iscsid-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_iscsid_service_enabled(systemd: Systemd):
    """Test that iscsid.service is enabled"""
    assert systemd.is_enabled("iscsid.service")


@pytest.mark.setting_ids(["GL-SET-iscsi-service-iscsid-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_iscsid_service_active(systemd: Systemd):
    """Test that iscsid.service is active"""
    assert systemd.is_active("iscsid.service")


@pytest.mark.setting_ids(["GL-SET-iscsi-service-tgt-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_tgt_service_enabled(systemd: Systemd):
    """Test that tgt.service is enabled"""
    assert systemd.is_enabled("tgt.service")


@pytest.mark.setting_ids(["GL-SET-iscsi-service-tgt-enable"])
@pytest.mark.feature("iscsi")
@pytest.mark.booted(reason="Requires systemd")
def test_iscsi_tgt_service_active(systemd: Systemd):
    """Test that tgt.service is active"""
    assert systemd.is_active("tgt.service")


# =============================================================================
# khost Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-khost-service-apparmor-enable"])
@pytest.mark.feature("khost")
@pytest.mark.booted(reason="Requires systemd")
def test_khost_apparmor_service_enabled(systemd: Systemd):
    """Test that apparmor.service is enabled"""
    assert systemd.is_enabled("apparmor.service")


@pytest.mark.setting_ids(["GL-SET-khost-service-apparmor-enable"])
@pytest.mark.feature("khost")
@pytest.mark.booted(reason="Requires systemd")
def test_khost_apparmor_service_active(systemd: Systemd):
    """Test that apparmor.service is active"""
    assert systemd.is_active("apparmor.service")


# =============================================================================
# lima Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-lima-service-sshd-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_ssh_service_enabled(systemd: Systemd):
    """Test that ssh.service is enabled"""
    assert systemd.is_enabled("ssh.service")


@pytest.mark.setting_ids(["GL-SET-lima-service-sshd-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_ssh_service_active(systemd: Systemd):
    """Test that ssh.service is active"""
    assert systemd.is_active("ssh.service")


# =============================================================================
# log Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-log-service-auditd-enable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_auditd_service_enabled(systemd: Systemd):
    """Test that auditd.service is enabled"""
    assert systemd.is_enabled("auditd.service")


@pytest.mark.setting_ids(["GL-SET-log-service-auditd-enable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_auditd_service_active(systemd: Systemd):
    """Test that auditd.service is active"""
    assert systemd.is_active("auditd.service")


@pytest.mark.setting_ids(["GL-SET-log-service-rsyslog-preset-disable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_rsyslog_service_disabled(systemd: Systemd):
    """Test that rsyslog.service is disabled by preset"""
    assert systemd.is_disabled("rsyslog.service")


@pytest.mark.setting_ids(["GL-SET-log-service-rsyslog-preset-disable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_rsyslog_service_inactive(systemd: Systemd):
    """Test that rsyslog.service is inactive"""
    assert systemd.is_inactive("rsyslog.service")


@pytest.mark.setting_ids(["GL-SET-log-service-systemd-journald-audit-socket-enable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_systemd_journald_audit_socket_service_enabled(systemd: Systemd):
    """Test that systemd-journald-audit.socket is enabled"""
    assert systemd.is_enabled("systemd-journald-audit.socket")


@pytest.mark.setting_ids(["GL-SET-log-service-systemd-journald-audit-socket-enable"])
@pytest.mark.feature("log")
@pytest.mark.booted(reason="Requires systemd")
def test_log_systemd_journald_audit_socket_service_active(systemd: Systemd):
    """Test that systemd-journald-audit.socket is active"""
    assert systemd.is_active("systemd-journald-audit.socket")


# =============================================================================
# metal Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-metal-service-ipmievd-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_ipmievd_service_enabled(systemd: Systemd):
    """Test that ipmievd.service is enabled"""
    assert systemd.is_enabled("ipmievd.service")


@pytest.mark.setting_ids(["GL-SET-metal-service-ipmievd-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu", reason="IPMI device is not available on QEMU and service will fail"
)
def test_metal_ipmievd_service_active(systemd: Systemd):
    """Test that ipmievd.service is active"""
    assert systemd.is_active("ipmievd.service")


@pytest.mark.setting_ids(["GL-SET-metal-service-mdmonitor-oneshot-timer-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_mdmonitor_oneshot_timer_enabled(systemd: Systemd):
    """Test that mdadm.service is enabled"""
    assert systemd.is_enabled("mdmonitor-oneshot.timer")


@pytest.mark.setting_ids(["GL-SET-metal-service-mdmonitor-oneshot-timer-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_mdmonitor_oneshot_timer_inactive(systemd: Systemd):
    """Test that mdmonitor-oneshot.timer is inactive"""
    assert systemd.is_inactive("mdmonitor-oneshot.timer")


@pytest.mark.setting_ids(["GL-SET-metal-service-smartmontools-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
@pytest.mark.hypervisor(
    "not qemu",
    reason="unit will has condition to not be enabled/started on virtualization",
)
def test_metal_smartd_service_enabled(systemd: Systemd):
    """Test that smartd.service is enabled"""
    assert systemd.is_enabled("smartd.service")


@pytest.mark.setting_ids(["GL-SET-metal-service-smartmontools-enable"])
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


@pytest.mark.setting_ids(["GL-SET-multipath-service-multipathd-enable"])
@pytest.mark.feature("multipath")
@pytest.mark.booted(reason="Requires systemd")
def test_multipath_multipathd_service_enabled(systemd: Systemd):
    """Test that multipathd.service is enabled"""
    assert systemd.is_enabled("multipathd.service")


@pytest.mark.setting_ids(["GL-SET-multipath-service-multipathd-enable"])
@pytest.mark.feature("multipath")
@pytest.mark.booted(reason="Requires systemd")
def test_multipath_multipathd_service_active(systemd: Systemd):
    """Test that multipathd.service is active"""
    assert systemd.is_active("multipathd.service")


# -----------------------------------------------------------------------------
# nvme Feature Unit Files
# -----------------------------------------------------------------------------


@pytest.mark.setting_ids(["GL-SET-nvme-service-nvme-hostid-unit"])
@pytest.mark.feature("nvme")
def test_nvme_hostid_unit_exists(file):
    """Test that nvme-hostid.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/nvme-hostid.service")


# =============================================================================
# openstackbaremetal Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-service-netplan-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackbaremetal_systemd_networkd_service_enabled(systemd: Systemd):
    """Test that systemd-networkd.service is enabled"""
    assert systemd.is_enabled("systemd-networkd.service")


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-service-netplan-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackbaremetal_systemd_networkd_service_active(systemd: Systemd):
    """Test that systemd-networkd.service is active"""
    assert systemd.is_active("systemd-networkd.service")


# =============================================================================
# sap Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-sap-service-auditd-enable"])
@pytest.mark.feature("sap")
@pytest.mark.booted(reason="Requires systemd")
def test_sap_auditd_service_enabled(systemd: Systemd):
    """Test that auditd.service is enabled"""
    assert systemd.is_enabled("auditd.service")


@pytest.mark.setting_ids(["GL-SET-sap-service-auditd-enable"])
@pytest.mark.feature("sap")
@pytest.mark.booted(reason="Requires systemd")
def test_sap_auditd_service_active(systemd: Systemd):
    """Test that auditd.service is active"""
    assert systemd.is_active("auditd.service")


# =============================================================================
# server Feature Services
# =============================================================================


@pytest.mark.setting_ids(
    [
        "GL-SET-server-config-service-systemd-coredump-override",
    ]
)
@pytest.mark.feature("server and not _prod")
def test_server_systemd_coredump_override_exists(file: File):
    """Test that systemd-coredump service override exists"""
    assert file.exists("/etc/systemd/system/systemd-coredump@.service.d/override.conf")


@pytest.mark.setting_ids(["GL-SET-server-service-systemd-coredump-enable"])
@pytest.mark.feature("server and not _prod")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_coredump_socket_active(systemd: Systemd):
    """Test that systemd-coredump.socket is enabled"""
    assert systemd.is_active("systemd-coredump.socket")


@pytest.mark.setting_ids(["GL-SET-server-service-kexec-load-unit"])
@pytest.mark.feature("server")
def test_server_kexec_load_unit_exists(file):
    """Test that kexec-load@.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/kexec-load@.service")


@pytest.mark.setting_ids(["GL-SET-server-service-cron-update-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_cron_update_service_inactive(systemd: Systemd):
    """Test that cron-update.service is inactive (oneshot service)"""
    assert systemd.is_inactive("cron-update.service")


@pytest.mark.setting_ids(["GL-SET-server-service-kexec-load-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_kexec_load_service_enabled(
    systemd: Systemd, kernel_versions: KernelVersions
):
    kernel_version = kernel_versions.get_running().version
    """Test that kexec-load@{kernel_version}.service is enabled"""
    assert systemd.is_enabled(f"kexec-load@{kernel_version}.service")


@pytest.mark.setting_ids(["GL-SET-server-service-kexec-load-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_kexec_load_service_inactive(
    systemd: Systemd, kernel_versions: KernelVersions
):
    kernel_version = kernel_versions.get_running().version
    """Test that kexec-load@{kernel_version}.service is inactive (oneshot service)"""
    assert systemd.is_inactive(f"kexec-load@{kernel_version}.service")


@pytest.mark.setting_ids(["GL-SET-server-service-sysstat-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_sysstat_service_enabled(systemd: Systemd):
    """Test that sysstat.service is enabled"""
    assert systemd.is_enabled("sysstat.service")


@pytest.mark.setting_ids(["GL-SET-server-service-sysstat-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_sysstat_service_active(systemd: Systemd):
    """Test that sysstat.service is active"""
    assert systemd.is_active("sysstat.service")


@pytest.mark.setting_ids(["GL-SET-server-service-systemd-networkd-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_networkd_service_enabled(systemd: Systemd):
    """Test that systemd-networkd.service is enabled"""
    assert systemd.is_enabled("systemd-networkd.service")


@pytest.mark.setting_ids(["GL-SET-server-service-systemd-networkd-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_networkd_service_active(systemd: Systemd):
    """Test that systemd-networkd.service is active"""
    assert systemd.is_active("systemd-networkd.service")


@pytest.mark.setting_ids(["GL-SET-server-service-systemd-repart-socket-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_repart_socket_active(systemd: Systemd):
    """Test that systemd-repart.socket is enabled"""
    assert systemd.is_active("systemd-repart.socket")


@pytest.mark.setting_ids(["GL-SET-server-service-systemd-resolved-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_resolved_service_enabled(systemd: Systemd):
    """Test that systemd-resolved.service is enabled"""
    assert systemd.is_enabled("systemd-resolved.service")


@pytest.mark.setting_ids(["GL-SET-server-service-systemd-resolved-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_resolved_service_active(systemd: Systemd):
    """Test that systemd-resolved.service is active"""
    assert systemd.is_active("systemd-resolved.service")


# =============================================================================
# ssh Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-ssh-service-ssh-keygen-unit"])
@pytest.mark.feature("ssh")
def test_ssh_keygen_unit_exists(file):
    """Test that ssh-keygen.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ssh-keygen.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-ssh-moduli-unit"])
@pytest.mark.feature("ssh")
def test_ssh_moduli_unit_exists(file):
    """Test that ssh-moduli.service unit file exists"""
    assert file.is_regular_file("/etc/systemd/system/ssh-moduli.service")


@pytest.mark.setting_ids(
    ["GL-SET-ssh-service-ssh-enable", "GL-SET-ssh-service-ssh-socket-preset-disable"]
)
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_socket_disabled(systemd: Systemd):
    """Test that ssh.socket is disabled by preset"""
    assert systemd.is_disabled("ssh.socket")


@pytest.mark.setting_ids(
    ["GL-SET-ssh-service-ssh-enable", "GL-SET-ssh-service-ssh-socket-preset-disable"]
)
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_socket_inactive(systemd: Systemd):
    """Test that ssh.service is inactive"""
    assert systemd.is_inactive("ssh.socket")


# TODO: enable if nftables or iptables is not available
# see: features/ssh/exec.config
# @pytest.mark.setting_ids([
#     "GL-SET-ssh-service-sshguard-enable",
#     "GL-SET-ssh-service-sshguard-preset-disable"
#     ])
# @pytest.mark.feature("ssh")
# @pytest.mark.booted(reason="Requires systemd")
# def test_ssh_sshguard_service_disabled(systemd: Systemd):
#     """Test that sshguard.service is disabled by preset"""
#     assert systemd.is_disabled("sshguard.service")
#
#
# @pytest.mark.setting_ids([
#     "GL-SET-ssh-service-sshguard-enable",
#     "GL-SET-ssh-service-sshguard-preset-disable"
#     ])
# @pytest.mark.feature("ssh")
# @pytest.mark.booted(reason="Requires systemd")
# def test_ssh_sshguard_service_inactive(systemd: Systemd):
#     """Test that sshguard.service is inactive"""
#     assert systemd.is_inactive("sshguard.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-ssh-keygen-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_keygen_service_enabled(systemd: Systemd):
    """Test that ssh-keygen.service is enabled"""
    assert systemd.is_enabled("ssh-keygen.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-ssh-keygen-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_keygen_service_active(systemd: Systemd):
    """Test that ssh-keygen.service is active"""
    assert systemd.is_active("ssh-keygen.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-sshguard-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_sshguard_service_enabled(systemd: Systemd):
    """Test that sshguard.service is enabled"""
    assert systemd.is_enabled("sshguard.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-sshguard-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_sshguard_service_active(systemd: Systemd):
    """Test that sshguard.service is active"""
    assert systemd.is_active("sshguard.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-auditd-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_auditd_service_enabled(systemd: Systemd):
    """Test that auditd.service is enabled"""
    assert systemd.is_enabled("auditd.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-auditd-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_auditd_service_active(systemd: Systemd):
    """Test that auditd.service is active"""
    assert systemd.is_active("auditd.service")


# =============================================================================
# vhost Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-vhost-service-libvirtd-socket-enable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_socket_service_enabled(systemd: Systemd):
    """Test that libvirtd.socket is enabled"""
    assert systemd.is_enabled("libvirtd.socket")


@pytest.mark.setting_ids(["GL-SET-vhost-service-libvirtd-socket-enable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_socket_service_active(systemd: Systemd):
    """Test that libvirtd.socket is active"""
    assert systemd.is_active("libvirtd.socket")


@pytest.mark.setting_ids(["GL-SET-vhost-service-libvirtd-tls-socket-preset-disable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_tls_socket_service_disabled(systemd: Systemd):
    """Test that libvirtd-tls.socket is disabled by preset"""
    assert systemd.is_disabled("libvirtd-tls.socket")


@pytest.mark.setting_ids(["GL-SET-vhost-service-libvirtd-tls-socket-preset-disable"])
@pytest.mark.feature("vhost")
@pytest.mark.booted(reason="Requires systemd")
def test_vhost_libvirtd_tls_socket_service_inactive(systemd: Systemd):
    """Test that libvirtd-tls.socket is inactive"""
    assert systemd.is_inactive("libvirtd-tls.socket")
