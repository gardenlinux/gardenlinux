locals {
  test_name                      = var.test_name
  test_name_safe                 = replace(local.test_name, "_", "-")
  test_name_very_safe            = replace(local.test_name_safe, "-", "")
  test_name_safe_short           = substr(local.test_name_safe, 0, 24)
  arch                           = var.arch == "amd64" ? "x86_64" : (var.arch == "arm64" ? "aarch64" : null)
  feature_tpm2                   = contains(var.features, "_tpm2")
  feature_trustedboot            = contains(var.features, "_trustedboot")
  image_name                     = "image-${local.test_name}.vhd"
  image_name_test                = "image-test-${local.test_name}.vhd"
  net_name                       = substr("net-${local.test_name}", 0, 63)
  subnet_name                    = substr("subnet-${local.test_name}", 0, 63)
  pip_name                       = substr("pip-${local.test_name}", 0, 63)
  nic_name                       = substr("nic-${local.test_name}", 0, 63)
  instance_name                  = substr("vm-${local.test_name_safe}", 0, 63)
  fw_name                        = substr("fw-${local.test_name}", 0, 63)
  router_name                    = "router-${local.test_name}"
  ssh_key_name                   = "ssh-${var.ssh_user}-${local.test_name}"
  ssh_private_key_file           = split(".pub", var.ssh_public_key)[0]
  ssh_parameters                 = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${local.ssh_private_key_file} -l ${var.ssh_user}"

  public_ip = openstack_networking_floatingip_v2.pip.address

  image_source_type = split("://", var.image_path)[0]
  image             = local.image_source_type == "file" ? "${split("file://", var.image_path)[1]}/${var.image_file}" : null
  image_test = "/gardenlinux/tests-ng/.build/tests-ng-dist.disk.qcow2"
}

# Get Public Network
data "openstack_networking_network_v2" "public" {
  name = var.public_network_name
}

# Create virtual network
resource "openstack_networking_network_v2" "net" {
  name                = local.net_name
}

# Create subnet
resource "openstack_networking_subnet_v2" "subnet" {
  name                 = local.subnet_name
  network_id           = openstack_networking_network_v2.net.id
  cidr                 = var.subnet_range
  ip_version           = 4
}

# Create public IPs
resource "openstack_networking_floatingip_v2" "pip" {
  pool                = var.floatingip_pool
}

resource "openstack_networking_floatingip_associate_v2" "pip_association" {
  floating_ip = openstack_networking_floatingip_v2.pip.address
  port_id     = openstack_networking_port_v2.nic.id
}

resource "openstack_networking_router_v2" "router" {
  name                = local.router_name
  external_network_id = data.openstack_networking_network_v2.public.id
  depends_on          = [openstack_networking_subnet_v2.subnet]
}

resource "openstack_networking_router_interface_v2" "router_interface" {
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.subnet.id
}

resource "openstack_networking_port_v2" "nic" {
  name = local.nic_name
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

resource "openstack_compute_keypair_v2" "key" {
  name = local.ssh_key_name
  public_key = file(var.ssh_public_key)
}

resource "openstack_images_image_v2" "image" {
  name = local.image_name
  local_file_path = local.image
  container_format = "bare"
  disk_format = "raw"
  min_disk_gb = 3
  min_ram_mb = 512
  properties = {
    architecture = local.arch
    cpu_arch = local.arch
    hypervisor_type = "qemu"
    image_description = "Garden Linux Platform Test"
    distro = "gardenlinux"
    os_distro = "gardenlinux"
    os_admin_user = var.ssh_user
    # setting this to "required" will give us "nova.exception.SecureBootNotSupported: Secure Boot is not supported by host"
    os_secure_boot = local.feature_trustedboot ? "optional" : null
    # setting a NVRAM template could be an option to boot with different OVMF_VARS.fd with PK/DB/DBX/KEK
    # this is undocumented and not working as of OpenStack 2024.1
    # the OVMF_VARS.fd and template would have to exist on the nova compute node
    # os_nvram_template = local.feature_trustedboot ? "/usr/share/qemu/firmware/99-edk2-x86_64-secure-enrolled-gl.json" : null
    hw_firmware_type = "uefi"
    hw_tpm_version = local.feature_tpm2 ? "2.0" : null
    hw_tpm_model= local.feature_tpm2 ? "tpm-tis" : null
  }
}

resource "openstack_images_image_v2" "image_test" {
  name = local.image_name_test
  local_file_path = local.image_test
  container_format = "bare"
  disk_format = "qcow2"
  min_disk_gb = 1
  min_ram_mb = 512
}

resource "openstack_blockstorage_volume_v3" "volume_test" {
  name = local.image_name_test
  size = 1
  image_id = openstack_images_image_v2.image_test.id
}

resource "openstack_compute_instance_v2" "instance" {
  name              = local.instance_name
  flavor_name       = var.instance_type
  # image_name        = "Garden Linux 1592.6"
  image_id          = openstack_images_image_v2.image.id
  key_pair          = openstack_compute_keypair_v2.key.name
  network {
    port = openstack_networking_port_v2.nic.id
  }
  block_device {
    uuid = openstack_blockstorage_volume_v3.volume_test.id
    source_type = "image"
    destination_type = "volume"
    boot_index = 1
    delete_on_termination = true
  }

  config_drive      = true
  # user_data = filebase64("vm-startup-script.sh")

  user_data = <<-EOT
#cloud-config
users:
  - name: ${var.ssh_user}
    lock_passwd: false
    passwd: $6$saltsalt$8659GkBs0jVaaGWWSWwC3tFAFJmSs7706M2bi0rUR2DE0rF8ypszUoAghSTcdvZz3r0hVg4882tKMLwMUogdD.
    ssh_authorized_keys:
      - ${file(var.ssh_public_key)}
    sudo: ALL=(ALL) NOPASSWD:ALL
    shell: /bin/bash
ssh_pwauth: true
runcmd:
  - touch /tmp/startup-script-ok
  - systemctl enable --now ssh
EOT

  depends_on = [
    openstack_networking_floatingip_v2.pip
  ]
}

resource "null_resource" "test_connect" {
  depends_on = [openstack_compute_instance_v2.instance]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = file(split(".pub", var.ssh_public_key)[0])
      host        = local.public_ip
      # usually this is created in /tmp but we have it mounted noexec
      script_path = "/home/${var.ssh_user}/terraform_%RAND%.sh"
      timeout     = "10m"
    }

    inline = [
      "cat /etc/os-release",
    ]
  }
}
