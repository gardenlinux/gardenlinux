data "alicloud_vswitches" "default" {
  name_regex = "vswitch-gardenlinux-platform-tests"
}

data "alicloud_security_groups" "default" {
  name_regex = "sg-gardenlinux-platform-tests"
}

resource "alicloud_vpc" "net" {
  ipv6_isp    = "BGP"
  description = local.net_name
  vpc_name    = local.net_name
  cidr_block  = var.provider_vars.net_cidr
  enable_ipv6 = true

  tags = merge(
    local.labels,
    { Name = local.net_name }
  )
}

resource "alicloud_vswitch" "subnet" {
  vswitch_name = local.subnet_name
  cidr_block   = var.provider_vars.subnet_cidr
  vpc_id       = alicloud_vpc.net.id
  zone_id      = data.alicloud_zones.zones.zones.0.id

  tags = merge(
    local.labels,
    { Name = local.subnet_name }
  )
}

resource "alicloud_security_group" "sg" {
  security_group_name = local.fw_name
  vpc_id = alicloud_vpc.net.id

  tags = merge(
    local.labels,
    { Name = local.fw_name },
    { sec-by-def-network-exception = "SSH" }
  )
}

resource "alicloud_security_group_rule" "sg-rule" {
  type              = "ingress"
  ip_protocol       = "tcp"
  nic_type          = "intranet"
  policy            = "accept"
  port_range        = "22/22"
  priority          = 1
  security_group_id = alicloud_security_group.sg.id
  cidr_ip           = "${var.my_ip}/32"
}
