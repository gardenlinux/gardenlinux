resource "terraform_data" "root_disk_hash" {
  count = var.existing_root_disk != "" ? 0 : 1
  input = {
    sha256 = filesha256(var.root_disk_path)
  }
}

resource "terraform_data" "test_disk_hash" {
  count = var.use_scp ? 0 : 1
  input = {
    sha256 = filesha256(var.test_disk_path)
  }
}

resource "alicloud_oss_bucket" "images" {
  count = var.existing_root_disk != "" ? 0 : 1

  bucket = local.bucket_name

  tags = merge(
    local.labels,
    { Name = local.bucket_name }
  )
}

resource "alicloud_oss_bucket_acl" "images_acl" {
  count = var.existing_root_disk != "" ? 0 : 1

  # depends_on = [alicloud_oss_bucket_ownership_controls.images_owner.0]

  bucket = alicloud_oss_bucket.images.0.id
  acl    = "private"
}

resource "alicloud_oss_bucket_public_access_block" "no_public_access" {
  count = var.existing_root_disk != "" ? 0 : 1

  bucket = alicloud_oss_bucket.images.0.id

  block_public_access = true
}

resource "alicloud_oss_bucket_server_side_encryption" "images_encryption" {
  count = var.existing_root_disk != "" ? 0 : 1

  bucket        = alicloud_oss_bucket.images.0.id
  sse_algorithm = "AES256"
}

resource "alicloud_oss_bucket_object" "image" {
  count = var.existing_root_disk != "" ? 0 : 1

  bucket = alicloud_oss_bucket.images.0.id
  key    = local.image_name
  source = replace(var.root_disk_path, ".raw", ".qcow2")
}

resource "alicloud_image_import" "import" {
  count = var.existing_root_disk != "" ? 0 : 1

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

resource "alicloud_oss_bucket_object" "image_test" {
  count = var.use_scp ? 0 : 1

  bucket = alicloud_oss_bucket.images.0.id
  key    = local.image_name
  source = var.test_disk_path
}

resource "alicloud_image_import" "import_test" {
  count = var.use_scp ? 0 : 1

  # architecture = local.arch
  # os_type      = "linux"
  # platform     = "Others Linux"
  license_type = "Auto"
  image_name   = "${local.image_name}-test"
  description  = "${local.image_name}-test"
  disk_device_mapping {
    # format = "qcow2"
    oss_bucket      = alicloud_oss_bucket.images.0.bucket
    oss_object      = alicloud_oss_bucket_object.image_test.0.key
    disk_image_size = 5
  }

}
data "alicloud_ecs_snapshots" "snapshots" {
  name_regex = "SnapshotForImage-${local.image_name}-test"

  depends_on = [
    alicloud_image_import.import_test
  ]
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
