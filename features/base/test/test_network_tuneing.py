import pytest
from helper.utils import check_for_kernel_setting
  

@pytest.mark.security_id(1121)
def test_ipv4(client, non_firecracker, non_chroot, non_container):
  """
     Test that we have IPv4 network settings to best options..

     net.ipv4.ip_forward
     Ensure that we can forward IPv4 packages. By default this is enabled.
     Defaul value is 1.

     tcp_max_syn_backlog 
     This is tracking open connections and will scale with the memory usage of the given Linux box.
     We set this to a lower set since is the time window between an open connection is establied,
     but not acknowledged. 
     Defaul value is 1.

     tcp_syncookies
     Prevent against the 'SYN flood attack', but considered a  fallback feature. Hence this could
     be disabled.
     Use tcp_max_syn_backlog, tcp_synack_retries or tcp_abort_on_overflow instead. 
     Defaul value is 1.

     icmp_echo_ignore_broadcasts
     Ignore nay ICMP broadcasts to avoid participating in Smurf attacks, since we're not in a
     conventional LAN there is no use-case for boradcasts ping. 
     Defaul value is 1.

     icmp_ignore_bogus_error_responses
     Some routes are nasty and sending bad icmp packages. By default the kernel would log this. We
     disalbe this. 
     Default value is 1.

     accept_source_route
     This is like a wildcard. This allows process of packages with a source list of IPs it want to
     be routed with. However, this might allow an attacker to redirect network traffic. 
     Our default setting is 0.

     default.accept_source_route
     Just like the parameter before, however, for the container uscase we need to enalbe it since
     every newer interface for a vm or container will direct this.  This is mandatory for a
     container setup since the different container want to have the ability to define it's routing
     via source list. 
     Our default setting is 1.

     rp_filter
     This is like a wildcard.  The  is for reverse path filtering. Necessary for container systems.
     This way a package remains router-able. We can have this to 0 for non testing, which is our
     default.  1 for strict testing or 2 for losely testing. 
     Default is 0.

     default.rp_filter
     Set the setting for unnamed devices that yet has to show. See the rp_filter for more insights.
     THis should share the same setting as before. 
     Default is 0.
     

  """
  list_of_ipv4_controls = [
     ("net.ipv4.net.ipv4.ip_forward"               ,'1'),
     ("net.ipv4.tcp_max_syn_backlog"            ,'2048'),
     ("net.ipv4.tcp_syncookies"                    ,'1'),
     ("net.ipv4.icmp_echo_ignore_broadcasts"       ,'1'),
     ("net.ipv4.icmp_ignore_bogus_error_responses" ,'1'),
     ("net.ipv4.conf.all.accept_source_route"      ,"0"),
     ("net.ipv4.conf.default.accept_source_route"  ,"1"),
     ("net.ipv4.conf.all.rp_filter"                ,"0"),
     ("net.ipv4.conf.default.rp_filter"            ,"0")]


  for control in list_of_ipv4_controls:
    control_value = check_for_kernel_setting(client, control[0])
    assert control[1] == control_value, f"Control {control[0]} does not have the right value. It's {control_value} and should be {control[1]}"
  

@pytest.mark.security_id(1122)
def test_ipv6(client, non_firecracker, non_chroot, non_container):
  """
     Test that we have IPv6 network settings to best options.

     disable_ipv6
     Disabling IPv6 is for a cloud use-case no options and since it's 2025 and 50% of the world
     speaks IPv6 this is out of the question.
     Default value is 0.

     default.disable_ipv6
     This is like a wildcard. We might have IPv6 enabled, but for any newer devices disabled.
     However, as of now this is always enabled.
     Default value is 1.

     net.ipv6.conf.all.forwarding
     This is like a wildcard.
     Default value is 1.

     net.ipv6.conf.all.accept_ra
     This option will set if we receive updates from the router regarind Router Advertisements, this
     way the network inform us about update in the network.
     Default value is 1.

     net.ipv6.conf.all.accept_redirects
     net.ipv6.conf.all.router_solicitations
     net.ipv6.conf.all.autoconf
     net.ipv6.conf.default.autoconf
     net.ipv6.conf.all.accept_dad
     net.ipv6.conf.all.dad_transmits
     net.ipv6.conf.default.dad_transmits
  """

  list_of_ipv6_controls = [
     ("net.ipv6.conf.all.disable_ipv6"             ,'0'),
     ("net.ipv6.conf.default.disable_ipv6"         ,'0'),
     ("net.ipv6.conf.all.forwarding"               ,'1'),
     ("net.ipv6.conf.default.accept_ra"            ,'1'),
     ("net.ipv6.conf.all.accept_redirects"         ,'1'),
     ("net.ipv6.conf.all.router_solicitations"    ,'-1'),
     ("net.ipv6.conf.all.autoconf"                 ,'1'),
     ("net.ipv6.conf.default.autoconf"             ,'1'),
     ("net.ipv6.conf.all.accept_dad"               ,'0'),
     ("net.ipv6.conf.default.accept_dad"           ,'1'),
     ("net.ipv6.conf.all.dad_transmits"            ,'1'),
     ("net.ipv6.conf.default.dad_transmits"        ,'1')

     ]


  for control in list_of_ipv6_controls:
    control_value = check_for_kernel_setting(client, control[0])
    assert control[1] == control_value, f"Control {control[0]} does not have the right value. It's {control_value} and should be {control[1]}"
