"""
Test systemd services for enabled and active states across all Garden Linux features.

This module tests that services required by various features are properly enabled
and active. Tests are organized by feature and follow the pattern of having separate
tests for enabled and active states.
"""

import pytest
from plugins.kernel_versions import KernelVersions
from plugins.systemd import Systemd

# =============================================================================
# _fwcfg Feature Services
# =============================================================================


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
    # TODO: This may be a oneshot service - verify if active test is appropriate
    assert systemd.is_active("qemu-fw_cfg-script.service")


# =============================================================================
# _ignite Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-_ignite-service-ignition-enable"])
@pytest.mark.feature("_ignite")
@pytest.mark.booted(reason="Requires systemd")
def test__ignite_ignition_service_enabled(systemd: Systemd):
    """Test that ignition.service is enabled"""
    assert systemd.is_enabled("ignition.service")


@pytest.mark.setting_ids(["GL-SET-_ignite-service-ignition-enable"])
@pytest.mark.feature("_ignite")
@pytest.mark.booted(reason="Requires systemd")
def test__ignite_ignition_service_active(systemd: Systemd):
    """Test that ignition.service is active"""
    # TODO: This may be a oneshot service - verify if active test is appropriate
    assert systemd.is_active("ignition.service")


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
# aide Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-init-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_aide_init_service_enabled(systemd: Systemd):
    """Test that aide-init.service is enabled"""
    assert systemd.is_enabled("aide-init.service")


@pytest.mark.setting_ids(["GL-SET-aide-service-aide-init-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_aide_init_service_active(systemd: Systemd):
    """Test that aide-init.service is active"""
    assert systemd.is_active("aide-init.service")


@pytest.mark.setting_ids(["GL-SET-aide-service-timer-aide-check-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_timer_aide_check_service_enabled(systemd: Systemd):
    """Test that aide-check.timer is enabled"""
    assert systemd.is_enabled("aide-check.timer")


@pytest.mark.setting_ids(["GL-SET-aide-service-timer-aide-check-enable"])
@pytest.mark.feature("aide")
@pytest.mark.booted(reason="Requires systemd")
def test_aide_timer_aide_check_service_active(systemd: Systemd):
    """Test that aide-check.timer is active"""
    assert systemd.is_active("aide-check.timer")


# =============================================================================
# ali Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-ali-service-cloud-init-local-enable"])
@pytest.mark.feature("ali")
@pytest.mark.booted(reason="Requires systemd")
def test_ali_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-ali-service-cloud-init-local-enable"])
@pytest.mark.feature("ali")
@pytest.mark.booted(reason="Requires systemd")
def test_ali_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# aws Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-aws-service-cloud-init-local-enable"])
@pytest.mark.feature("aws")
@pytest.mark.hypervisor("amazon", reason="Requires Amazon AWS infrastructure")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-aws-service-cloud-init-local-enable"])
@pytest.mark.feature("aws")
@pytest.mark.booted(reason="Requires systemd")
def test_aws_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


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
# azure Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-azure-service-cloud-init-local-enable"])
@pytest.mark.feature("azure")
@pytest.mark.booted(reason="Requires systemd")
def test_azure_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-azure-service-cloud-init-local-enable"])
@pytest.mark.feature("azure")
@pytest.mark.booted(reason="Requires systemd")
def test_azure_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# checkbox Feature Services
# =============================================================================


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


@pytest.mark.setting_ids(["GL-SET-chost-service-dbus-user-session-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_dbus_user_session_service_enabled(systemd: Systemd):
    """Test that dbus-user-session.service is enabled"""
    assert systemd.is_enabled("dbus-user-session.service")


@pytest.mark.setting_ids(["GL-SET-chost-service-dbus-user-session-enable"])
@pytest.mark.feature("chost")
@pytest.mark.booted(reason="Requires systemd")
def test_chost_dbus_user_session_service_active(systemd: Systemd):
    """Test that dbus-user-session.service is active"""
    assert systemd.is_active("dbus-user-session.service")


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


@pytest.mark.setting_ids(["GL-SET-fedramp-service-chrony-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_chrony_service_enabled(systemd: Systemd):
    """Test that chrony.service is enabled"""
    assert systemd.is_enabled("chrony.service")


@pytest.mark.setting_ids(["GL-SET-fedramp-service-chrony-enable"])
@pytest.mark.feature("fedramp")
@pytest.mark.booted(reason="Requires systemd")
def test_fedramp_chrony_service_active(systemd: Systemd):
    """Test that chrony.service is active"""
    assert systemd.is_active("chrony.service")


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
def test_gcp_google_guest_agent_service_active(systemd: Systemd):
    """Test that google-guest-agent.service is active"""
    assert systemd.is_active("google-guest-agent.service")


@pytest.mark.setting_ids(["GL-SET-gcp-service-chrony-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_chrony_service_enabled(systemd: Systemd):
    """Test that chrony.service is enabled"""
    assert systemd.is_enabled("chrony.service")


@pytest.mark.setting_ids(["GL-SET-gcp-service-chrony-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_chrony_service_active(systemd: Systemd):
    """Test that chrony.service is active"""
    assert systemd.is_active("chrony.service")


@pytest.mark.setting_ids(["GL-SET-gcp-service-cloud-init-local-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-gcp-service-cloud-init-local-enable"])
@pytest.mark.feature("gcp")
@pytest.mark.booted(reason="Requires systemd")
def test_gcp_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# iscsi Feature Services
# =============================================================================


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
# kvm Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-kvm-service-ignition-disable-enable"])
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_ignition_disable_service_enabled(systemd: Systemd):
    """Test that ignition-disable.service is enabled"""
    assert systemd.is_enabled("ignition-disable.service")


@pytest.mark.setting_ids(["GL-SET-kvm-service-ignition-disable-enable"])
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_ignition_disable_service_active(systemd: Systemd):
    """Test that ignition-disable.service is active"""
    # TODO: This may be a oneshot service - verify if active test is appropriate
    assert systemd.is_active("ignition-disable.service")


@pytest.mark.setting_ids(["GL-SET-kvm-service-qemu-guest-agent-enable"])
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_qemu_guest_agent_service_enabled(systemd: Systemd):
    """Test that qemu-guest-agent.service is enabled"""
    assert systemd.is_enabled("qemu-guest-agent.service")


@pytest.mark.setting_ids(["GL-SET-kvm-service-qemu-guest-agent-enable"])
@pytest.mark.feature("kvm")
@pytest.mark.booted(reason="Requires systemd")
def test_kvm_qemu_guest_agent_service_active(systemd: Systemd):
    """Test that qemu-guest-agent.service is active"""
    assert systemd.is_active("qemu-guest-agent.service")


# =============================================================================
# lima Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-lima-service-cloud-init-local-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-lima-service-cloud-init-local-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-lima-service-qemu-guest-agent-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_qemu_guest_agent_service_enabled(systemd: Systemd):
    """Test that qemu-guest-agent.service is enabled"""
    assert systemd.is_enabled("qemu-guest-agent.service")


@pytest.mark.setting_ids(["GL-SET-lima-service-qemu-guest-agent-enable"])
@pytest.mark.feature("lima")
@pytest.mark.booted(reason="Requires systemd")
def test_lima_qemu_guest_agent_service_active(systemd: Systemd):
    """Test that qemu-guest-agent.service is active"""
    assert systemd.is_active("qemu-guest-agent.service")


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
    # TODO: Socket-activated service - verify if active test is appropriate
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
def test_metal_ipmievd_service_active(systemd: Systemd):
    """Test that ipmievd.service is active"""
    assert systemd.is_active("ipmievd.service")


@pytest.mark.setting_ids(["GL-SET-metal-service-mdadm-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_mdadm_service_enabled(systemd: Systemd):
    """Test that mdadm.service is enabled"""
    assert systemd.is_enabled("mdadm.service")


@pytest.mark.setting_ids(["GL-SET-metal-service-mdadm-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_mdadm_service_active(systemd: Systemd):
    """Test that mdadm.service is active"""
    assert systemd.is_active("mdadm.service")


@pytest.mark.setting_ids(["GL-SET-metal-service-smartmontools-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
def test_metal_smartd_service_enabled(systemd: Systemd):
    """Test that smartd.service is enabled"""
    assert systemd.is_enabled("smartd.service")


@pytest.mark.setting_ids(["GL-SET-metal-service-smartmontools-enable"])
@pytest.mark.feature("metal")
@pytest.mark.booted(reason="Requires systemd")
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


# =============================================================================
# openstack Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-openstack-service-cloud-init-local-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstack_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-openstack-service-cloud-init-local-enable"])
@pytest.mark.feature("openstack")
@pytest.mark.booted(reason="Requires systemd")
def test_openstack_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


# =============================================================================
# openstackbaremetal Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-service-cloud-init-local-enable"])
@pytest.mark.feature("openstackbaremetal")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackbaremetal_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-openstackbaremetal-service-cloud-init-local-enable"])
@pytest.mark.feature("openstackbaremetal")
@pytest.mark.booted(reason="Requires systemd")
def test_openstackbaremetal_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")


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


@pytest.mark.setting_ids(["GL-SET-server-service-systemd-repart-enable"])
@pytest.mark.feature("server")
@pytest.mark.booted(reason="Requires systemd")
def test_server_systemd_repart_service_active(systemd: Systemd):
    """Test that systemd-repart.service is inactive (oneshot service with remain-after-exit=yes)"""
    assert systemd.is_active("systemd-repart.service")


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


@pytest.mark.setting_ids(["GL-SET-ssh-service-ssh-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_service_enabled(systemd: Systemd):
    """Test that ssh.service is enabled"""
    assert systemd.is_enabled("ssh.service")


@pytest.mark.setting_ids(["GL-SET-ssh-service-ssh-enable"])
@pytest.mark.feature("ssh")
@pytest.mark.booted(reason="Requires systemd")
def test_ssh_ssh_service_active(systemd: Systemd):
    """Test that ssh.service is active"""
    assert systemd.is_active("ssh.service")


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
    # TODO: This may be a oneshot service - verify if active test is appropriate
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
    # TODO: Socket-activated service - verify if active test is appropriate
    assert systemd.is_active("libvirtd.socket")


# =============================================================================
# vmware Feature Services
# =============================================================================


@pytest.mark.setting_ids(["GL-SET-vmware-service-cloud-init-local-enable"])
@pytest.mark.feature("vmware")
@pytest.mark.booted(reason="Requires systemd")
def test_vmware_cloud_init_local_service_enabled(systemd: Systemd):
    """Test that cloud-init-local.service is enabled"""
    assert systemd.is_enabled("cloud-init-local.service")


@pytest.mark.setting_ids(["GL-SET-vmware-service-cloud-init-local-enable"])
@pytest.mark.feature("vmware")
@pytest.mark.booted(reason="Requires systemd")
def test_vmware_cloud_init_local_service_inactive(systemd: Systemd):
    """Test that cloud-init-local.service is inactive"""
    assert systemd.is_inactive("cloud-init-local.service")
