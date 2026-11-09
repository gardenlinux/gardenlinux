resource "stackit_key_pair" "key" {
  name       = local.ssh_key_name
  public_key = file(var.ssh_public_key_path)
}

resource "stackit_server" "instance" {
  project_id        = var.provider_vars.project_id
  name              = local.test_name
  availability_zone = var.provider_vars.availability_zone
  machine_type      = local.machine_type

  boot_volume = {
    source_type = "image"
    source_id   = local.use_existing_root_disk ? var.existing_root_disk : stackit_image.image[0].image_id
    size        = 10
  }

  keypair_name = stackit_key_pair.key.name

  network_interfaces = [stackit_network_interface.nic.network_interface_id]

  user_data = base64encode(file(var.user_data_script_path))

  labels = local.labels

  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash,
      terraform_data.test_disk_hash,
    ]
  }
}

output "vm_ip" {
  value       = stackit_public_ip.pip.ip
  description = "Public IPv4 of the VM"
}

output "ssh_user" {
  value       = var.provider_vars.ssh_user
}

output "image_requirements" {
  value       = var.image_requirements
  description = "Image requirements"
}
