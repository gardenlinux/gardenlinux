data "openstack_networking_network_v2" "public" {
  name = var.provider_vars.public_net_name
}

# Create virtual network
resource "openstack_networking_network_v2" "net" {
  name                = local.net_name
}

# Create subnet
resource "openstack_networking_subnet_v2" "subnet" {
  name                 = local.subnet_name
  network_id           = openstack_networking_network_v2.net.id
  cidr                 = var.provider_vars.subnet_cidr
  ip_version           = 4
}

# Create public IPs
resource "openstack_networking_floatingip_v2" "pip" {
  pool                = var.provider_vars.floatingip_pool
}

resource "openstack_networking_floatingip_associate_v2" "pip_association" {
  floating_ip = openstack_networking_floatingip_v2.pip.address
  port_id     = openstack_networking_port_v2.nic.id
}

resource "openstack_networking_router_v2" "router" {
  name                = "${local.test_name}-router"
  external_network_id = data.openstack_networking_network_v2.public.id
  depends_on          = [openstack_networking_subnet_v2.subnet]
}

resource "openstack_networking_router_interface_v2" "router_interface" {
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.subnet.id
}

resource "openstack_networking_port_v2" "nic" {
  name = "${local.test_name}-nic"
  network_id = openstack_networking_network_v2.net.id
  fixed_ip {
    subnet_id = openstack_networking_subnet_v2.subnet.id
  }
  security_group_ids = [openstack_networking_secgroup_v2.sg.id]
}

resource "openstack_networking_secgroup_v2" "sg" {
  name        = local.fw_name
  depends_on  = [openstack_networking_router_v2.router]
}

resource "openstack_networking_secgroup_rule_v2" "sg_icmp" {
  direction         = "ingress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
  protocol          = "icmp"
  security_group_id = openstack_networking_secgroup_v2.sg.id
}

resource "openstack_networking_secgroup_rule_v2" "sg_ssh" {
  description       = "ssh"
  direction         = "ingress"
  ethertype         = "IPv4"
  remote_ip_prefix  = "0.0.0.0/0"
  protocol          = "tcp"
  port_range_min    = 22
  port_range_max    = 22
  security_group_id = openstack_networking_secgroup_v2.sg.id
}
