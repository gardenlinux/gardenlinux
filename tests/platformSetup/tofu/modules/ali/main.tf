locals {
  test_name            = var.test_name
  test_name_safe       = replace(local.test_name, "_", "-")
  test_name_safe_short = substr(local.test_name_safe, 0, 24)
  # feature_tpm2 = contains(var.features, "tpm2")
  # feature_trustedboot = contains(var.features, "trustedboot")
  # boot_mode            = local.feature_tpm2 ? "uefi" : "legacy-bios"
  arch                 = var.arch == "amd64" ? "x86_64" : var.arch
  bucket_name          = lower(replace(substr(strrev(base64encode(local.test_name)), 0, 64), "=", "0")) # be unique max 64 chars
  image_name           = "image-${local.test_name}"
  image_name_test      = "image-test-${local.test_name}"
  net_name             = "net-${local.test_name}"
  subnet_name          = "subnet-${local.test_name}"
  instance_name        = "instance-${local.test_name}"
  fw_name              = "fw-${local.test_name}"
  disk_os_name         = "disk-os-${local.test_name}"
  ssh_key_name         = "ssh-${var.ssh_user}-${local.test_name}"
  ssh_private_key_file = split(".pub", var.ssh_public_key)[0]
  ssh_parameters       = "-o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i ${local.ssh_private_key_file} -l ${var.ssh_user}"
  public_ip            = alicloud_instance.instance.public_ip
  labels = {
    component = "gardenlinux"
    test-type = "platform-test"
    test-name = local.test_name
  }
  labels_name = {
    Name = local.test_name
  }

  image_source_type = split("://", var.image_path)[0]
  image = (
    local.image_source_type == "file" ? "${split("file://", var.image_path)[1]}/${var.image_file}" :
    local.image_source_type == "cloud" ? var.image_file :
    null
  )
  image_test = "/gardenlinux/tests-ng/.build/tests-ng-dist.disk.raw"
}

data "alicloud_account" "current" {
}

data "alicloud_caller_identity" "current" {
}

data "alicloud_zones" "zones" {
  available_resource_creation = "VSwitch"
}

resource "alicloud_oss_bucket" "images" {
  count = 1

  bucket = local.bucket_name

  tags = merge(
    local.labels,
    { Name = local.bucket_name }
  )
}

resource "alicloud_oss_bucket_acl" "images_acl" {
  count = 1

  # depends_on = [alicloud_oss_bucket_ownership_controls.images_owner.0]

  bucket = alicloud_oss_bucket.images.0.id
  acl    = "private"
}

# resource "alicloud_oss_bucket_policy" "images_policy" {
#   count = local.image_source_type == "file" ? 1 : 0
#
#   bucket = alicloud_oss_bucket.images.id
#   policy    = <<POLICY
# {
#   "Version": "1",
#   "Statement": [
#     {
#       "Principal": [
#         "*"
#       ],
#       "Effect": "Deny",
#       "Action": [
#         "oss:*"
#       ],
#       "Resource": [
#         "acs:oss:*:${data.alicloud_account.current.id}:${alicloud_oss_bucket.images.0.bucket}",
#         "acs:oss:*:${data.alicloud_account.current.id}:${alicloud_oss_bucket.images.0.bucket}/*"
#       ]
#     }
#   ]
# }
# POLICY
#
#   depends_on = [alicloud_oss_bucket.images.0]
# }

resource "alicloud_oss_bucket_public_access_block" "no_public_access" {
  count = 1

  bucket = alicloud_oss_bucket.images.0.id

  block_public_access = true
}

resource "alicloud_oss_bucket_server_side_encryption" "images_encryption" {
  count = 1

  bucket        = alicloud_oss_bucket.images.0.id
  sse_algorithm = "AES256"
}

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
  cidr_block  = var.net_range
  enable_ipv6 = true

  tags = merge(
    local.labels,
    { Name = local.net_name }
  )
}

resource "alicloud_vswitch" "subnet" {
  vswitch_name = local.subnet_name
  cidr_block   = var.subnet_range
  vpc_id       = alicloud_vpc.net.id
  zone_id      = data.alicloud_zones.zones.zones.0.id

  tags = merge(
    local.labels,
    { Name = local.subnet_name }
  )
}

resource "alicloud_security_group" "sg" {
  name   = local.fw_name
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

resource "alicloud_oss_bucket_object" "image" {
  count = local.image_source_type == "file" ? 1 : 0

  bucket = alicloud_oss_bucket.images.0.id
  key    = local.image_name
  source = local.image
}

resource "alicloud_oss_bucket_object" "image_test" {
  count = 1

  bucket = alicloud_oss_bucket.images.0.id
  key    = local.image_name_test
  source = local.image_test
}

resource "alicloud_image_import" "import" {
  count = local.image_source_type == "file" ? 1 : 0

  architecture = local.arch
  os_type      = "linux"
  platform     = "Others Linux"
  license_type = "Auto"
  image_name   = local.image_name
  description  = local.image_name
  disk_device_mapping {
    # format = "qcow2"
    oss_bucket      = alicloud_oss_bucket.images.0.bucket
    oss_object      = alicloud_oss_bucket_object.image.0.key
    disk_image_size = 5
  }
}

resource "alicloud_image_import" "import_test" {
  count = 1

  # architecture = local.arch
  # os_type      = "linux"
  # platform     = "Others Linux"
  license_type = "Auto"
  image_name   = local.image_name_test
  description  = local.image_name_test
  disk_device_mapping {
    # format = "qcow2"
    oss_bucket      = alicloud_oss_bucket.images.0.bucket
    oss_object      = alicloud_oss_bucket_object.image_test.0.key
    disk_image_size = 5
  }

}
data "alicloud_ecs_snapshots" "snapshots" {
  name_regex = "SnapshotForImage-${local.image_name_test}"
}

resource "alicloud_disk" "test_disk" {
  count = 1

  snapshot_id = data.alicloud_ecs_snapshots.snapshots.snapshots.0.id
  availability_zone = data.alicloud_zones.zones.zones.0.id
  size = 20
  category = "cloud_efficiency"

  depends_on = [
    alicloud_image_import.import_test
  ]
}

resource "alicloud_disk_attachment" "disk_attachment_test" {
  count = 1

  disk_id     = alicloud_disk.test_disk.0.id
  instance_id = alicloud_instance.instance.id
}

resource "alicloud_ecs_key_pair" "ssh_key" {
  key_pair_name = local.ssh_key_name
  public_key    = file(var.ssh_public_key)

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
  instance_type              = var.instance_type
  image_id = (
    local.image_source_type == "file" ? alicloud_image_import.import.0.id :
    local.image_source_type == "cloud" ? var.image_file :
    null
  )
  instance_name              = local.instance_name
  vswitch_id                 = alicloud_vswitch.subnet.id
  internet_max_bandwidth_out = 1

  system_disk_category    = "cloud_auto"
  system_disk_name        = local.disk_os_name
  system_disk_size        = 20
  system_disk_description = local.image_name

  instance_charge_type = "PostPaid"

  user_data = file("vm-startup-script.sh")

  tags = merge(
    local.labels,
    { Name = local.instance_name }
  )
}

resource "null_resource" "test_disk_mount" {
  depends_on = [alicloud_disk_attachment.disk_attachment_test]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = file(split(".pub", var.ssh_public_key)[0])
      host        = local.public_ip
      # usually this is created in /tmp but we have it mounted noexec
      script_path = "/home/${var.ssh_user}/terraform_%RAND%.sh"
      timeout     = "20m"
    }

    inline = [
      "sudo mount /dev/vdb /mnt",
    ]
  }
}

resource "null_resource" "test_connect" {
  depends_on = [alicloud_instance.instance]

  provisioner "remote-exec" {
    connection {
      type        = "ssh"
      user        = var.ssh_user
      private_key = file(split(".pub", var.ssh_public_key)[0])
      host        = local.public_ip
      # usually this is created in /tmp but we have it mounted noexec
      script_path = "/home/${var.ssh_user}/terraform_%RAND%.sh"
      timeout     = "20m"
    }

    inline = [
      "cat /etc/os-release",
    ]
  }
}
