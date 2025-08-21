resource "openstack_compute_keypair_v2" "key" {
  name = local.ssh_key_name
  public_key = file(var.ssh_public_key_path)
}

resource "openstack_compute_instance_v2" "instance" {
  name              = local.test_name
  flavor_name       = local.instance_type
  image_id          = openstack_images_image_v2.image.id
  key_pair          = openstack_compute_keypair_v2.key.name
  network {
    port = openstack_networking_port_v2.nic.id
  }

  config_drive      = true
  user_data = filebase64(var.user_data_script_path)

  depends_on = [
    openstack_networking_floatingip_v2.pip
  ]

  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash,
      terraform_data.test_disk_hash,
    ]
  }
}

output "vm_ip" {
  value       = openstack_networking_floatingip_v2.pip.address
  description = "Public IPv4 of the VM"
}

output "ssh_user" {
  value       = var.provider_vars.ssh_user
}
