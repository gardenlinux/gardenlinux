resource "terraform_data" "root_disk_hash" {
  count = var.existing_root_disk != "" ? 0 : 1
  input = {
    sha256 = filesha256(var.root_disk_path)
  }
}

resource "terraform_data" "test_disk_hash" {
  input = {
    sha256 = filesha256(var.test_disk_path)
  }
}

resource "alicloud_oss_bucket" "images" {
  count = var.existing_root_disk != "" ? 0 : 1

  bucket = local.bucket_name

  server_side_encryption_rule {
    sse_algorithm = "AES256"
  }

  tags = merge(
    local.labels,
    { Name = local.bucket_name }
  )
}

resource "terraform_data" "pause_1_second" {
  triggers_replace = [
    alicloud_oss_bucket_images.id
  ]

  provisioner "local-exec" {
    command = "sleep 1"
  }
}

resource "alicloud_oss_bucket_public_access_block" "no_public_access" {
  count = var.existing_root_disk != "" ? 0 : 1

  bucket = alicloud_oss_bucket.images[0].bucket

  block_public_access = true

  depends_on = [terraform_data.pause_1_second]
}

resource "alicloud_oss_bucket_object" "image" {
  count = var.existing_root_disk != "" ? 0 : 1

  bucket = alicloud_oss_bucket.images[0].bucket
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
    oss_bucket      = alicloud_oss_bucket.images[0].bucket
    oss_object      = alicloud_oss_bucket_object.image[0].key
    disk_image_size = 5
    # format = "qcow2" # seems broken as it diffs to QCOW2 (capital)
  }

  lifecycle {
    replace_triggered_by = [
      terraform_data.root_disk_hash
    ]
  }
}

resource "alicloud_oss_bucket_object" "image_test" {
  bucket = alicloud_oss_bucket.images[0].bucket
  key    = "${local.image_name}-test"
  ## somehow qcow2 does not work
  # source = replace(var.test_disk_path, ".raw", ".qcow2")
  source = var.test_disk_path
}

resource "alicloud_image_import" "import_test" {
  image_name  = "${local.image_name}-test"
  description = "${local.image_name}-test"
  disk_device_mapping {
    oss_bucket      = alicloud_oss_bucket.images[0].bucket
    oss_object      = alicloud_oss_bucket_object.image_test.key
    disk_image_size = 5
    # format = "qcow2" # seems broken as it diffs to QCOW2 (capital)
  }

  lifecycle {
    replace_triggered_by = [
      terraform_data.test_disk_hash
    ]
  }
}

data "alicloud_ecs_snapshots" "image_test" {
  name_regex = "SnapshotForImage-${local.image_name}-test"

  depends_on = [
    alicloud_image_import.import_test
  ]
}
