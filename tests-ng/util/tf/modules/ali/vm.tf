resource "alicloud_ecs_key_pair" "ssh_key" {
  key_pair_name = local.ssh_key_name
  public_key    = file(var.ssh_public_key_path)

  tags = merge(
    local.labels,
    { Name = local.ssh_key_name }
  )
}

resource "alicloud_ecs_key_pair_attachment" "ssh_key" {
  key_pair_name = alicloud_ecs_key_pair.ssh_key.key_pair_name
  instance_ids  = [alicloud_instance.instance.id]
  force         = true
}

resource "alicloud_instance" "instance" {
  availability_zone          = data.alicloud_zones.zones.zones.0.id
  security_groups            = [alicloud_security_group.sg.id]
  instance_type              = local.instance_type
  image_id = (
    var.existing_root_disk != "" ? var.existing_root_disk :
    var.existing_root_disk == "" ? alicloud_image_import.import.0.id :
    null
  )
  instance_name              = local.test_name
  vswitch_id                 = alicloud_vswitch.subnet.id
  internet_max_bandwidth_out = 1

  system_disk_category    = "cloud_auto"
  system_disk_name        = local.image_name
  system_disk_size        = 20
  system_disk_description = local.image_name

  instance_charge_type = "PostPaid"

  user_data = file(var.user_data_script_path)

  tags = merge(
    local.labels,
    { Name = local.test_name }
  )
}

output "vm_ip" {
  value       = alicloud_instance.instance.public_ip
  description = "Public IPv4 of the VM"
}

output "ssh_user" {
  value       = var.provider_vars.ssh_user
}
