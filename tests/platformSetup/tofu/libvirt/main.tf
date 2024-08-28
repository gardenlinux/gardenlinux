data "external" "my_ip" {
  program = ["curl", "-q", "https://api.ipify.org?format=json"]
}

provider "libvirt" {
  uri = var.qemu_uri
}

locals {
  my_ip = data.external.my_ip.result.ip
  uuid = uuid()
  # bucket_name   = "images-${var.test_name}"
  # tar_name      = "image-${var.test_name}.tar.gz"
  # image_name    = "image-${var.test_name}"
  net_name      = "net-${var.test_name}"
  subnet_name   = "subnet-${var.test_name}"
  sa_name       = "sa-${var.test_name}"
  instance_name = "instance-${var.test_name}"
  fw_name = "fw-${var.test_name}"
  ssh_private_key_file = split(".pub", var.ssh_public_key)[0]
  ssh_parameters = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${local.ssh_private_key_file} -l ${var.ssh_user}"
  public_ip = libvirt_domain.instance.network_interface.0.addresses.0
  labels = {
    component =  "gardenlinux"
    test-type =  "platform-test"
    test-name =  var.test_name
    test-uuid =  local.uuid
  }

  # get "file" or "s3" from image_source
  image_source_type = split("://", var.image_source)[0]
  # s3_bucket         = local.image_source_type == "s3" ? split("/", var.image_source)[2] : null
  # s3_key            = local.image_source_type == "s3" ? split("/objects/", var.image_source)[1] : null
  # image_file = local.image_source_type == "file" ? split("file://", var.image_source)[1] : (local.image_source_type == "s3" ? local_file.downloaded_s3_image[0].filename : null)

  image_file = local.image_source_type == "file" ? split("file://", var.image_source)[1] : null
}

resource "libvirt_pool" "pool" {
  name = var.test_name
  type = "dir"
  # path = dirname(var.image_source)
  # path = dirname(local.image_file)
  path = "/tmp/${var.test_name}"
}

resource "libvirt_volume" "volume" {
  # name   = basename(var.image_source)
  source = local.image_file
  name   = "${basename(local.image_file)}.qcow2"
  pool   = libvirt_pool.pool.name
}

resource "libvirt_cloudinit_disk" "cloudinit" {
  name      = "cloudinit-${var.test_name}"
  user_data = <<EOF
#cloud-config
users:
  - name: ${var.ssh_user}
    ssh-authorized-keys:
      - ${jsonencode(trimspace(file("${var.ssh_public_key}")))}
EOF
}

# data "template_file" "user_data" {
#   template = file("${path.module}/cloud_init.cfg")
# }

resource "libvirt_network" "network" {
  name = var.test_name
  # mode can be: "nat" (default), "none", "route", "open", "bridge"
  mode = "nat"
  # mode = "bridge"
  # bridge = "gl0"
  addresses = [var.subnet_range]
  dhcp {
   enabled = true
  }
}

resource "libvirt_domain" "instance" {
  name   = var.test_name
  memory = var.instance_memory
  vcpu   = var.instance_cpu

  qemu_agent = true

  # arch = "x86_64"
  # machine = "q35"
  firmware = var.uefi_firmware

  boot_device {
    dev = ["hd"]
  }

  disk {
    volume_id = libvirt_volume.volume.id
  }

  # network_interface {
  #   macvtap = var.macvtap_device
  #   wait_for_lease = true
  # }

  network_interface {
    network_id = libvirt_network.network.id
    hostname = "gardenlinux"
    # addresses = ["10.242.10.1"]
    wait_for_lease = true
  }

  cloudinit = libvirt_cloudinit_disk.cloudinit.id

}

resource "null_resource" "add_ssh_key" {
  provisioner "local-exec" {
    command = "./qemu-agent-guest-copy-to ${var.qemu_uri} ${libvirt_domain.instance.name} ${var.ssh_public_key} /home/${var.ssh_user}/.ssh/authorized_keys; ./qemu-agent-guest-exec ${var.qemu_uri} ${libvirt_domain.instance.name} chmod 0600 /home/${var.ssh_user}/.ssh/authorized_keys; ./qemu-agent-guest-exec ${var.qemu_uri} ${libvirt_domain.instance.name} chown ${var.ssh_user} /home/${var.ssh_user}/.ssh/authorized_keys"
  }

  triggers = {
    instance_changed = libvirt_domain.instance.id
  }

  # depends_on = [libvirt_domain.instance]
}
