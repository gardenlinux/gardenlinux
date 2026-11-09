resource "stackit_network" "net" {
  project_id = var.provider_vars.project_id
  name       = local.net_name

  ipv4_prefix = var.provider_vars.net_cidr

  labels = local.labels
}

resource "stackit_network_interface" "nic" {
  project_id = var.provider_vars.project_id
  network_id = stackit_network.net.network_id
  name       = "${local.test_name}-nic"

  security_group_ids = [stackit_security_group.sg.security_group_id]
}

resource "stackit_public_ip" "pip" {
  project_id = var.provider_vars.project_id

  labels = local.labels
}

resource "stackit_public_ip_associate" "pip_association" {
  project_id           = var.provider_vars.project_id
  public_ip_id         = stackit_public_ip.pip.public_ip_id
  network_interface_id = stackit_network_interface.nic.network_interface_id
}

resource "stackit_security_group" "sg" {
  project_id = var.provider_vars.project_id
  name       = local.fw_name

  labels = local.labels
}

resource "stackit_security_group_rule" "sg_icmp" {
  project_id        = var.provider_vars.project_id
  security_group_id = stackit_security_group.sg.security_group_id
  direction         = "ingress"
  protocol          = { name = "icmp" }
  ip_range          = "0.0.0.0/0"
}

resource "stackit_security_group_rule" "sg_ssh" {
  project_id        = var.provider_vars.project_id
  security_group_id = stackit_security_group.sg.security_group_id
  direction         = "ingress"
  protocol          = { name = "tcp" }
  port_range = {
    min = 22
    max = 22
  }
  ip_range = "0.0.0.0/0"
}
